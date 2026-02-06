# Building a Device Management Agent for IoT with AgentCore

![AgentCore Gateway](images/gateway-article.webp)

> In *The Hitchhiker's Guide to the Galaxy*, the ships of the Vogon Constructor Fleet were tracked, catalogued, and managed with ruthless bureaucratic efficiency. Every vessel had a registry entry. Every status change was logged. The fleet operated across vast stretches of space with centralized command and control. Your IoT fleet is the same problem -- except your devices are smaller, less likely to demolish planets, and considerably harder to get on the phone.

## The Problem

Your fleet has 10,000 sensors deployed across three factory floors. A technician radios in: "Line 7 pressure readings look off." What follows is a familiar ritual -- the ops engineer opens the IoT console, searches for the device by its cryptic ID, checks its shadow state, cross-references the last telemetry batch in DynamoDB, verifies the firmware version, and then manually issues a recalibration command through a separate CLI tool. Twenty minutes later, they confirm the fix. Meanwhile, two more anomaly alerts fire on different devices.

IoT device management at scale is a workflow problem disguised as an infrastructure problem. The individual operations -- querying device state, sending commands, updating configurations, reviewing telemetry history -- are all straightforward API calls. The challenge is that a human operator must stitch these calls together in real time, holding the full context of the fleet in their head while triaging multiple issues simultaneously.

This tutorial builds an **IoT device management agent** on AgentCore that puts natural language in front of your device fleet. An operator says "Check the pressure sensor on Line 7 and recalibrate it if it's drifting," and the agent handles the rest: looking up the device, reading its state from DynamoDB, issuing the command through a Lambda function, and confirming the result. Think of it as building your own *Hitchhiker's Guide* for your device fleet -- a comprehensive, searchable, and occasionally opinionated database of everything you need to know about every device in your operation.

The architecture uses three AgentCore services working together:

- **Gateway** converts Lambda functions into MCP tools that the agent can discover and invoke
- **Identity** integrates with Amazon Cognito so only authenticated operators can interact with the fleet
- **Runtime** deploys the agent with microVM isolation and session persistence

Every tool call flows through a real Lambda function backed by a real DynamoDB table. No simulated responses.

## Prerequisites

### AWS Account Setup

- AWS account with Bedrock AgentCore access enabled
- IAM permissions: `bedrock-agentcore:*`, `bedrock:InvokeModel`, `lambda:*`, `dynamodb:*`, `cognito-idp:*`, `iam:*`
- Region: us-east-1

### Local Environment

- Python 3.10+
- pip for package management
- AWS CLI configured with valid credentials

### Required Packages

```bash
# requirements.txt
boto3>=1.34.0
strands-agents>=0.1.0
bedrock-agentcore-sdk>=1.0.0
python-dotenv>=1.0.0
```

## Getting Started

### Step 1: Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Environment

```python
import os
import json
import time
import boto3
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
ACCOUNT_ID = boto3.client('sts').get_caller_identity()['Account']

# Clients
dynamodb = boto3.resource('dynamodb', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)
iam = boto3.client('iam', region_name=REGION)
cognito = boto3.client('cognito-idp', region_name=REGION)
control = boto3.client('bedrock-agentcore-control', region_name=REGION)
data = boto3.client('bedrock-agentcore', region_name=REGION)
```

### Step 3: Create the DynamoDB Device Table

The device table stores the current state of every device in the fleet. Each item represents a single device with its metadata, configuration, last known telemetry, and status.

```python
# Create DynamoDB table for device state
dynamodb_client = boto3.client('dynamodb', region_name=REGION)

dynamodb_client.create_table(
    TableName='iot-devices',
    KeySchema=[
        {'AttributeName': 'device_id', 'KeyType': 'HASH'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'device_id', 'AttributeType': 'S'},
        {'AttributeName': 'location', 'AttributeType': 'S'}
    ],
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'location-index',
            'KeySchema': [
                {'AttributeName': 'location', 'KeyType': 'HASH'}
            ],
            'Projection': {'ProjectionType': 'ALL'},
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

# Wait for table to be active
waiter = dynamodb_client.get_waiter('table_exists')
waiter.wait(TableName='iot-devices')
print("DynamoDB table 'iot-devices' is active")
```

Seed it with some representative devices so the agent has something to work with. Every good galactic registry needs initial entries -- even the Guide itself started with a handful of field researchers filing reports about planets before it became the most widely consulted reference work in the known universe:

```python
table = dynamodb.Table('iot-devices')

devices = [
    {
        'device_id': 'SENSOR-LINE7-PRESS-001',
        'device_type': 'pressure_sensor',
        'location': 'factory-floor-1/line-7',
        'firmware_version': '2.4.1',
        'status': 'online',
        'last_telemetry': {
            'pressure_psi': '142.7',
            'temperature_c': '38.2',
            'timestamp': '2025-07-15T10:30:00Z'
        },
        'configuration': {
            'sample_rate_seconds': '5',
            'alert_threshold_psi': '150',
            'calibration_date': '2025-06-01'
        },
        'registered_at': '2024-11-20T08:00:00Z'
    },
    {
        'device_id': 'SENSOR-LINE7-TEMP-002',
        'device_type': 'temperature_sensor',
        'location': 'factory-floor-1/line-7',
        'firmware_version': '2.4.1',
        'status': 'online',
        'last_telemetry': {
            'temperature_c': '72.5',
            'humidity_pct': '45.2',
            'timestamp': '2025-07-15T10:29:55Z'
        },
        'configuration': {
            'sample_rate_seconds': '10',
            'alert_threshold_c': '80',
            'calibration_date': '2025-05-15'
        },
        'registered_at': '2024-11-20T08:05:00Z'
    },
    {
        'device_id': 'ACTUATOR-LINE3-VALVE-001',
        'device_type': 'valve_actuator',
        'location': 'factory-floor-1/line-3',
        'firmware_version': '3.1.0',
        'status': 'online',
        'last_telemetry': {
            'position_pct': '75',
            'flow_rate_lpm': '120.3',
            'timestamp': '2025-07-15T10:30:02Z'
        },
        'configuration': {
            'max_position_pct': '100',
            'emergency_shutoff': 'enabled',
            'control_mode': 'automatic'
        },
        'registered_at': '2024-09-10T14:00:00Z'
    },
    {
        'device_id': 'GATEWAY-FLOOR2-001',
        'device_type': 'edge_gateway',
        'location': 'factory-floor-2',
        'firmware_version': '4.0.2',
        'status': 'warning',
        'last_telemetry': {
            'connected_devices': '47',
            'cpu_pct': '82.1',
            'memory_pct': '71.3',
            'uptime_hours': '2184',
            'timestamp': '2025-07-15T10:30:01Z'
        },
        'configuration': {
            'max_connections': '50',
            'telemetry_batch_interval_seconds': '30',
            'firmware_auto_update': 'false'
        },
        'registered_at': '2024-06-01T09:00:00Z'
    },
    {
        'device_id': 'SENSOR-LINE3-VIBR-001',
        'device_type': 'vibration_sensor',
        'location': 'factory-floor-1/line-3',
        'firmware_version': '1.8.3',
        'status': 'offline',
        'last_telemetry': {
            'vibration_mm_s': '4.2',
            'frequency_hz': '120',
            'timestamp': '2025-07-14T23:15:00Z'
        },
        'configuration': {
            'sample_rate_seconds': '1',
            'alert_threshold_mm_s': '8.0',
            'calibration_date': '2025-04-01'
        },
        'registered_at': '2025-01-15T11:30:00Z'
    }
]

with table.batch_writer() as batch:
    for device in devices:
        batch.put_item(Item=device)

print(f"Seeded {len(devices)} devices into iot-devices table")
```

### Step 4: Create the Lambda Function for Device Management

This Lambda function is the backbone of the agent's tool set. It handles three operations -- `get_device_status`, `list_devices`, and `send_command` -- each mapped to a DynamoDB operation. Gateway routes MCP tool calls to this function, and the function dispatches based on the tool name in the event payload.

```python
lambda_code = '''
import json
import boto3
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("iot-devices")


def lambda_handler(event, context):
    """MCP tool handler for IoT device management.

    Gateway sends events with:
      - name: the tool name (get_device_status, list_devices, send_command)
      - arguments: dict of tool arguments
    """
    tool_name = event.get("name")
    arguments = event.get("arguments", {})

    handlers = {
        "get_device_status": handle_get_device_status,
        "list_devices": handle_list_devices,
        "send_command": handle_send_command,
    }

    handler = handlers.get(tool_name)
    if not handler:
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
        }

    try:
        result = handler(arguments)
        return {"content": [{"type": "text", "text": json.dumps(result, default=str)}]}
    except Exception as e:
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Error in {tool_name}: {str(e)}"}],
        }


def handle_get_device_status(args):
    """Get current status and telemetry for a single device."""
    device_id = args.get("device_id")
    if not device_id:
        raise ValueError("device_id is required")

    response = table.get_item(Key={"device_id": device_id})
    item = response.get("Item")

    if not item:
        return {"error": f"Device {device_id} not found"}

    return {
        "device_id": item["device_id"],
        "device_type": item.get("device_type"),
        "location": item.get("location"),
        "status": item.get("status"),
        "firmware_version": item.get("firmware_version"),
        "last_telemetry": item.get("last_telemetry", {}),
        "configuration": item.get("configuration", {}),
    }


def handle_list_devices(args):
    """List devices, optionally filtered by location or status."""
    location = args.get("location")
    status_filter = args.get("status")
    device_type = args.get("device_type")

    if location:
        response = table.query(
            IndexName="location-index",
            KeyConditionExpression=Key("location").eq(location),
        )
        items = response.get("Items", [])
    else:
        scan_kwargs = {}
        filter_expressions = []

        if status_filter:
            filter_expressions.append(Attr("status").eq(status_filter))
        if device_type:
            filter_expressions.append(Attr("device_type").eq(device_type))

        if filter_expressions:
            combined = filter_expressions[0]
            for expr in filter_expressions[1:]:
                combined = combined & expr
            scan_kwargs["FilterExpression"] = combined

        response = table.scan(**scan_kwargs)
        items = response.get("Items", [])

    devices = []
    for item in items:
        devices.append(
            {
                "device_id": item["device_id"],
                "device_type": item.get("device_type"),
                "location": item.get("location"),
                "status": item.get("status"),
                "firmware_version": item.get("firmware_version"),
            }
        )

    return {"devices": devices, "count": len(devices)}


def handle_send_command(args):
    """Send a command to a device and update its state in DynamoDB."""
    device_id = args.get("device_id")
    command = args.get("command")
    parameters = args.get("parameters", {})

    if not device_id or not command:
        raise ValueError("device_id and command are required")

    # Verify device exists
    response = table.get_item(Key={"device_id": device_id})
    item = response.get("Item")
    if not item:
        return {"error": f"Device {device_id} not found"}

    if item.get("status") == "offline":
        return {
            "error": f"Device {device_id} is offline. Command cannot be delivered.",
            "device_id": device_id,
            "command": command,
            "delivered": False,
        }

    timestamp = datetime.now(timezone.utc).isoformat()

    # Process command and update device state
    update_expr_parts = ["#last_command = :cmd", "#last_command_at = :ts"]
    expr_names = {
        "#last_command": "last_command",
        "#last_command_at": "last_command_at",
    }
    expr_values = {
        ":cmd": {"command": command, "parameters": parameters, "status": "delivered"},
        ":ts": timestamp,
    }

    if command == "recalibrate":
        update_expr_parts.append("#config.#cal_date = :cal_date")
        expr_names["#config"] = "configuration"
        expr_names["#cal_date"] = "calibration_date"
        expr_values[":cal_date"] = timestamp[:10]

    elif command == "update_config":
        for key, value in parameters.items():
            safe_key = key.replace("-", "_")
            update_expr_parts.append(f"#config.#param_{safe_key} = :param_{safe_key}")
            expr_names["#config"] = "configuration"
            expr_names[f"#param_{safe_key}"] = key
            expr_values[f":param_{safe_key}"] = str(value)

    elif command == "reboot":
        update_expr_parts.append("#status = :status")
        expr_names["#status"] = "status"
        expr_values[":status"] = "rebooting"

    elif command == "set_status":
        new_status = parameters.get("status", "online")
        update_expr_parts.append("#status = :status")
        expr_names["#status"] = "status"
        expr_values[":status"] = new_status

    table.update_item(
        Key={"device_id": device_id},
        UpdateExpression="SET " + ", ".join(update_expr_parts),
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
    )

    return {
        "device_id": device_id,
        "command": command,
        "parameters": parameters,
        "delivered": True,
        "timestamp": timestamp,
    }
'''

# Write Lambda code to a file for deployment
import zipfile
import io

zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('lambda_function.py', lambda_code)
zip_buffer.seek(0)

# Create IAM role for Lambda
lambda_trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

lambda_role = iam.create_role(
    RoleName='iot-device-agent-lambda-role',
    AssumeRolePolicyDocument=json.dumps(lambda_trust_policy)
)

# Attach DynamoDB and CloudWatch policies
iam.attach_role_policy(
    RoleName='iot-device-agent-lambda-role',
    PolicyArn='arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess'
)
iam.attach_role_policy(
    RoleName='iot-device-agent-lambda-role',
    PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
)

# Wait for role propagation
time.sleep(10)

# Create Lambda function
lambda_client.create_function(
    FunctionName='iot-device-management',
    Runtime='python3.12',
    Role=lambda_role['Role']['Arn'],
    Handler='lambda_function.lambda_handler',
    Code={'ZipFile': zip_buffer.read()},
    Timeout=30,
    MemorySize=256,
    Environment={
        'Variables': {
            'TABLE_NAME': 'iot-devices'
        }
    }
)

# Wait for function to be active
time.sleep(5)
print("Lambda function 'iot-device-management' created")
```

Let us walk through what the Lambda handler does for each tool. Like the sub-etha network that keeps every ship in the galaxy connected, this single Lambda function is the communications backbone for your entire device fleet:

**`get_device_status`** -- Takes a `device_id` and performs a `GetItem` on DynamoDB. Returns the full device record including telemetry, configuration, and metadata. This is the agent's primary way to inspect a single device.

**`list_devices`** -- Supports three optional filters: `location` (uses the GSI for efficient queries), `status`, and `device_type` (both use scan with filter expressions). Returns a summary of matching devices. When the agent needs to find "all offline devices" or "every sensor on Line 7," this is the tool it reaches for.

**`send_command`** -- The write path. Takes a `device_id`, a `command` string, and optional `parameters`. It first validates the device exists and is not offline, then executes the command by updating the DynamoDB record. Supported commands include:

- `recalibrate` -- Updates the calibration date in the device configuration
- `update_config` -- Modifies arbitrary configuration parameters
- `reboot` -- Sets the device status to `rebooting`
- `set_status` -- Changes the device status (e.g., marking a device for maintenance)

In a production system, `send_command` would also publish to an IoT Core MQTT topic to deliver the command to the physical device. For this tutorial, the DynamoDB update serves as the authoritative record of the command.

### Step 5: Set Up Cognito for Operator Authentication

Factory operators need to authenticate before interacting with the device fleet. Cognito provides the user pool and issues JWT tokens that Gateway validates on every request.

```python
# Create Cognito User Pool
user_pool = cognito.create_user_pool(
    PoolName='iot-device-operators',
    Policies={
        'PasswordPolicy': {
            'MinimumLength': 12,
            'RequireUppercase': True,
            'RequireLowercase': True,
            'RequireNumbers': True,
            'RequireSymbols': True
        }
    },
    AutoVerifiedAttributes=['email'],
    Schema=[
        {
            'Name': 'email',
            'Required': True,
            'Mutable': True,
            'AttributeDataType': 'String'
        },
        {
            'Name': 'custom:role',
            'Required': False,
            'Mutable': True,
            'AttributeDataType': 'String',
            'StringAttributeConstraints': {
                'MinLength': '1',
                'MaxLength': '50'
            }
        }
    ]
)

user_pool_id = user_pool['UserPool']['Id']
print(f"Cognito User Pool created: {user_pool_id}")

# Create app client for the agent
app_client = cognito.create_user_pool_client(
    UserPoolId=user_pool_id,
    ClientName='iot-agent-client',
    GenerateSecret=False,
    ExplicitAuthFlows=[
        'ALLOW_USER_PASSWORD_AUTH',
        'ALLOW_REFRESH_TOKEN_AUTH',
        'ALLOW_USER_SRP_AUTH'
    ],
    SupportedIdentityProviders=['COGNITO'],
    AllowedOAuthFlows=['code', 'implicit'],
    AllowedOAuthScopes=['openid', 'email', 'profile'],
    AllowedOAuthFlowsUserPoolClient=True,
    CallbackURLs=['https://localhost/callback']
)

client_id = app_client['UserPoolClient']['ClientId']
print(f"App client created: {client_id}")

# Create a test operator user
cognito.admin_create_user(
    UserPoolId=user_pool_id,
    Username='operator-01',
    UserAttributes=[
        {'Name': 'email', 'Value': 'operator@example.com'},
        {'Name': 'email_verified', 'Value': 'true'},
        {'Name': 'custom:role', 'Value': 'fleet_operator'}
    ],
    TemporaryPassword='TempPass123!@#',
    MessageAction='SUPPRESS'
)

# Set permanent password
cognito.admin_set_user_password(
    UserPoolId=user_pool_id,
    Username='operator-01',
    Password='Operator!SecurePass789',
    Permanent=True
)

print("Test operator user created: operator-01")
```

The OIDC discovery URL that Gateway needs for JWT validation follows a standard format based on the user pool ID:

```python
discovery_url = (
    f"https://cognito-idp.{REGION}.amazonaws.com/{user_pool_id}"
    f"/.well-known/openid-configuration"
)
print(f"OIDC Discovery URL: {discovery_url}")
```

### Step 6: Create the Gateway with JWT Authentication

Now we wire everything together. The Gateway acts as the MCP endpoint that the agent connects to for tool access. It validates JWTs from Cognito on inbound requests and routes tool calls to the Lambda function.

```python
# Create IAM role for Gateway
gateway_trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

gateway_role = iam.create_role(
    RoleName='iot-device-gateway-role',
    AssumeRolePolicyDocument=json.dumps(gateway_trust_policy)
)

# Allow Gateway to invoke the Lambda function
iam.put_role_policy(
    RoleName='iot-device-gateway-role',
    PolicyName='InvokeLambdaPolicy',
    PolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": "lambda:InvokeFunction",
            "Resource": f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:iot-device-management"
        }]
    })
)

time.sleep(10)

# Create Gateway with Cognito JWT authentication
gateway = control.create_gateway(
    name='IoTDeviceGateway',
    description='MCP gateway for IoT device management tools',
    roleArn=gateway_role['Role']['Arn'],
    authorizerType='CUSTOM_JWT',
    authorizerConfiguration={
        'customJwtAuthorizerConfig': {
            'discoveryUrl': discovery_url,
            'allowedAudiences': [client_id],
            'allowedClients': [client_id]
        }
    },
    protocolType='MCP',
    searchConfiguration={
        'searchType': 'SEMANTIC'
    }
)

gateway_id = gateway['gatewayId']
print(f"Gateway created: {gateway_id}")

# Wait for gateway to become active
for _ in range(60):
    gw_status = control.get_gateway(gatewayIdentifier=gateway_id)
    if gw_status['status'] in ('ACTIVE', 'READY'):
        break
    time.sleep(2)
print(f"Gateway status: {gw_status['status']}")
```

### Step 7: Add Device Management Tools to the Gateway

Each Lambda tool gets a schema that tells the agent what arguments it accepts and what the tool does. Clear descriptions matter here -- the agent's model uses these descriptions to decide which tool to call for a given request.

```python
LAMBDA_ARN = f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:iot-device-management"

control.create_gateway_target(
    gatewayIdentifier=gateway_id,
    name='IoTDeviceTools',
    targetConfiguration={
        'lambdaTargetConfiguration': {
            'lambdaArn': LAMBDA_ARN,
            'toolSchema': {
                'tools': [
                    {
                        'name': 'get_device_status',
                        'description': (
                            'Get the current status, telemetry readings, configuration, '
                            'and metadata for a specific IoT device. Use this to inspect '
                            'a single device by its device ID.'
                        ),
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'device_id': {
                                    'type': 'string',
                                    'description': (
                                        'The unique device identifier '
                                        '(e.g., SENSOR-LINE7-PRESS-001)'
                                    )
                                }
                            },
                            'required': ['device_id']
                        }
                    },
                    {
                        'name': 'list_devices',
                        'description': (
                            'List IoT devices in the fleet with optional filters. '
                            'Can filter by physical location (e.g., factory-floor-1/line-7), '
                            'device status (online, offline, warning, rebooting), or '
                            'device type (pressure_sensor, temperature_sensor, '
                            'valve_actuator, edge_gateway, vibration_sensor). '
                            'Returns a summary of matching devices.'
                        ),
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'location': {
                                    'type': 'string',
                                    'description': (
                                        'Filter by physical location '
                                        '(e.g., factory-floor-1/line-7)'
                                    )
                                },
                                'status': {
                                    'type': 'string',
                                    'description': 'Filter by device status',
                                    'enum': ['online', 'offline', 'warning', 'rebooting']
                                },
                                'device_type': {
                                    'type': 'string',
                                    'description': 'Filter by device type',
                                    'enum': [
                                        'pressure_sensor',
                                        'temperature_sensor',
                                        'valve_actuator',
                                        'edge_gateway',
                                        'vibration_sensor'
                                    ]
                                }
                            }
                        }
                    },
                    {
                        'name': 'send_command',
                        'description': (
                            'Send an operational command to a specific IoT device. '
                            'Supported commands: recalibrate (recalibrate sensors), '
                            'reboot (restart the device), update_config (change device '
                            'configuration parameters), set_status (change device status). '
                            'The device must be online to receive commands.'
                        ),
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'device_id': {
                                    'type': 'string',
                                    'description': 'The device to send the command to'
                                },
                                'command': {
                                    'type': 'string',
                                    'description': 'The command to execute',
                                    'enum': [
                                        'recalibrate',
                                        'reboot',
                                        'update_config',
                                        'set_status'
                                    ]
                                },
                                'parameters': {
                                    'type': 'object',
                                    'description': (
                                        'Optional parameters for the command. '
                                        'For update_config: key-value pairs of config '
                                        'to change. For set_status: {"status": "value"}.'
                                    )
                                }
                            },
                            'required': ['device_id', 'command']
                        }
                    }
                ]
            }
        }
    }
)

print("Device management tools added to gateway")
```

### Step 8: Build the Agent

The agent wraps the Gateway tools with a system prompt tuned for IoT operations. It uses Strands as the framework and Claude as the model. The tool functions make real calls through the Gateway MCP interface.

```python
from strands import Agent, tool
from strands.models import BedrockModel

model = BedrockModel(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    region_name=REGION
)


@tool
def get_device_status(device_id: str) -> str:
    """Get current status, telemetry, and configuration for a specific IoT device.

    Args:
        device_id: The unique device identifier (e.g., SENSOR-LINE7-PRESS-001)
    """
    response = data.invoke_gateway(
        gatewayIdentifier=gateway_id,
        method='tools/call',
        payload=json.dumps({
            'name': 'get_device_status',
            'arguments': {'device_id': device_id}
        }).encode()
    )
    return json.loads(response['payload'].read())


@tool
def list_devices(location: str = "", status: str = "", device_type: str = "") -> str:
    """List IoT devices with optional filters.

    Args:
        location: Filter by physical location (e.g., factory-floor-1/line-7)
        status: Filter by status (online, offline, warning, rebooting)
        device_type: Filter by type (pressure_sensor, temperature_sensor, etc.)
    """
    arguments = {}
    if location:
        arguments['location'] = location
    if status:
        arguments['status'] = status
    if device_type:
        arguments['device_type'] = device_type

    response = data.invoke_gateway(
        gatewayIdentifier=gateway_id,
        method='tools/call',
        payload=json.dumps({
            'name': 'list_devices',
            'arguments': arguments
        }).encode()
    )
    return json.loads(response['payload'].read())


@tool
def send_command(device_id: str, command: str, parameters: dict = {}) -> str:
    """Send a command to an IoT device.

    Args:
        device_id: The device to send the command to
        command: Command to execute (recalibrate, reboot, update_config, set_status)
        parameters: Optional parameters for the command
    """
    response = data.invoke_gateway(
        gatewayIdentifier=gateway_id,
        method='tools/call',
        payload=json.dumps({
            'name': 'send_command',
            'arguments': {
                'device_id': device_id,
                'command': command,
                'parameters': parameters
            }
        }).encode()
    )
    return json.loads(response['payload'].read())


# Create the IoT device management agent
iot_agent = Agent(
    model=model,
    tools=[get_device_status, list_devices, send_command],
    system_prompt="""You are an IoT device management assistant for factory operations.
You help operators monitor, troubleshoot, and manage their device fleet.

Follow these rules:
1. Always check device status before sending commands.
2. Never send commands to offline devices -- inform the operator instead.
3. When asked about a location, list devices there first to give a complete picture.
4. Confirm destructive commands (reboot, recalibrate) by showing the device state first.
5. Report telemetry with units (PSI, Celsius, mm/s, etc.).
6. If a device shows warning status, proactively mention it.
7. Summarize results clearly with device IDs, locations, and relevant readings.

Available commands:
- recalibrate: Recalibrate a sensor (updates calibration date)
- reboot: Restart a device (sets status to rebooting)
- update_config: Change configuration parameters (pass key-value pairs)
- set_status: Change device status (pass {"status": "value"})"""
)
```

### Step 9: Authenticate and Run Locally

Before deploying, test the agent locally. Authenticate through Cognito to get a JWT, then run a few representative queries.

```python
# Authenticate operator through Cognito
auth_response = cognito.initiate_auth(
    ClientId=client_id,
    AuthFlow='USER_PASSWORD_AUTH',
    AuthParameters={
        'USERNAME': 'operator-01',
        'PASSWORD': 'Operator!SecurePass789'
    }
)

id_token = auth_response['AuthenticationResult']['IdToken']
access_token = auth_response['AuthenticationResult']['AccessToken']
print("Operator authenticated successfully")

# Test: Check a specific device
response = iot_agent("What is the status of the pressure sensor on Line 7?")
print(response)
```

Expected output:

```
I checked the pressure sensor SENSOR-LINE7-PRESS-001 on Line 7. Here is the current status:

**Device:** SENSOR-LINE7-PRESS-001
**Type:** Pressure Sensor
**Location:** factory-floor-1/line-7
**Status:** Online
**Firmware:** 2.4.1

**Latest Telemetry:**
- Pressure: 142.7 PSI
- Temperature: 38.2 C
- Last reading: 2025-07-15 at 10:30 UTC

**Configuration:**
- Sample rate: every 5 seconds
- Alert threshold: 150 PSI
- Last calibrated: 2025-06-01

The device is operating normally. The pressure reading of 142.7 PSI is below
the alert threshold of 150 PSI.
```

```python
# Test: Find all offline devices
response = iot_agent("Are any devices offline right now?")
print(response)
```

Expected output:

```
I found 1 offline device in the fleet:

**SENSOR-LINE3-VIBR-001** (Vibration Sensor)
- Location: factory-floor-1/line-3
- Firmware: 1.8.3
- Last telemetry: 2025-07-14 at 23:15 UTC (over 11 hours ago)
- Last reading: 4.2 mm/s at 120 Hz

This device has been offline since last night. The last telemetry reading was
within normal range (4.2 mm/s, well below the 8.0 mm/s alert threshold), so
the issue is likely a connectivity problem rather than a sensor failure.

Would you like me to check the edge gateway for that floor or take any action?
```

```python
# Test: Recalibrate a device
response = iot_agent("Recalibrate the pressure sensor on Line 7")
print(response)
```

Expected output:

```
Let me first check the current status of the pressure sensor before recalibrating.

**SENSOR-LINE7-PRESS-001** is online and reporting:
- Pressure: 142.7 PSI
- Last calibrated: 2025-06-01 (44 days ago)

Proceeding with recalibration...

Recalibration command sent successfully:
- **Device:** SENSOR-LINE7-PRESS-001
- **Command:** recalibrate
- **Status:** Delivered
- **New calibration date:** 2025-07-15

The sensor will perform its recalibration routine. This typically takes
2-3 minutes. The calibration date has been updated in the device configuration.
```

### Step 10: Deploy to Runtime

Wrap the agent in the AgentCore Runtime application and deploy it.

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint()
async def handle_request(request):
    """Handle incoming IoT management requests."""
    prompt = request.get("prompt", "")
    operator_id = request.get("operator_id", "unknown")
    session_id = request.get("session_id", "default")

    # Include operator context in the prompt
    context_prompt = (
        f"[Operator: {operator_id}, Session: {session_id}]\n{prompt}"
    )

    response = iot_agent(context_prompt)
    return {
        "response": str(response),
        "operator_id": operator_id,
        "session_id": session_id
    }

if __name__ == "__main__":
    app.run()
```

Deploy with a generous timeout -- device operations may involve multiple sequential tool calls:

```bash
agentcore deploy --name iot-device-agent --memory 1024 --timeout 3600
```

### Step 11: Invoke the Deployed Agent

```bash
# Check a device
agentcore invoke '{
    "prompt": "Show me all devices on Line 7 and their current readings",
    "operator_id": "operator-01",
    "session_id": "shift-2025-07-15-morning"
}'

# Troubleshoot an alert
agentcore invoke '{
    "prompt": "The edge gateway on Floor 2 is showing a warning. What is going on and should we be concerned?",
    "operator_id": "operator-01",
    "session_id": "shift-2025-07-15-morning"
}'

# Batch operation
agentcore invoke '{
    "prompt": "Find all pressure sensors that have not been calibrated in the last 30 days and recalibrate them",
    "operator_id": "operator-01",
    "session_id": "shift-2025-07-15-morning"
}'
```

## Architecture

```
        Operator (Cognito JWT)
                |
                v
       [AgentCore Runtime]
       (microVM isolation)
                |
         [IoT Device Agent]
         (Strands + Claude)
                |
                v
       [AgentCore Gateway]
      (JWT auth + MCP tools)
     /          |          \
    v           v           v
get_device   list_      send_
_status      devices    command
    \          |          /
     v         v         v
   [Lambda: iot-device-management]
                |
                v
     [DynamoDB: iot-devices]
     (Device state + telemetry)
```

The data flow works like this:

1. The operator authenticates through Cognito and receives a JWT
2. The request hits Runtime, which spawns an isolated microVM session
3. The Strands agent receives the natural language prompt and plans tool calls
4. Each tool call flows through Gateway, which validates the JWT and routes to Lambda
5. The Lambda function reads from or writes to the DynamoDB device table
6. Results flow back through Gateway to the agent, which synthesizes a response

## Extending the Agent

### Adding IoT Core Integration

In a production deployment, `send_command` should publish to AWS IoT Core so commands reach physical devices over MQTT. Add this to the Lambda handler:

```python
import boto3

iot_data = boto3.client('iot-data', region_name='us-east-1')

def publish_command_to_device(device_id, command, parameters):
    """Publish command to device's MQTT topic via IoT Core."""
    topic = f"devices/{device_id}/commands"
    payload = json.dumps({
        'command': command,
        'parameters': parameters,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

    iot_data.publish(
        topic=topic,
        qos=1,
        payload=payload.encode()
    )
    return True
```

### Adding Telemetry History

Store historical telemetry in a time-series-friendly structure for trend analysis. Add a second DynamoDB table:

```python
dynamodb_client.create_table(
    TableName='iot-telemetry-history',
    KeySchema=[
        {'AttributeName': 'device_id', 'KeyType': 'HASH'},
        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'device_id', 'AttributeType': 'S'},
        {'AttributeName': 'timestamp', 'AttributeType': 'S'}
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)
```

Then add a `get_telemetry_history` tool to the Gateway target so the agent can analyze trends over time.

### Adding Cedar Policies for Command Authorization

Use AgentCore Policy to enforce rules about which operators can execute which commands. For example, restrict `reboot` commands to senior operators:

```
permit(
    principal,
    action == Action::"CallTool",
    resource == Tool::"send_command"
) when {
    context.arguments.command != "reboot"
};

permit(
    principal,
    action == Action::"CallTool",
    resource == Tool::"send_command"
) when {
    context.arguments.command == "reboot" &&
    principal.role == "senior_operator"
};
```

This ensures the recalibrate and update_config commands are available to all authenticated operators, but reboot requires the `senior_operator` role -- enforced deterministically at the Gateway boundary, not by the agent's prompt.

## Key Benefits

### Natural Language Fleet Management

Operators interact with devices using plain language instead of memorizing device IDs, CLI commands, and console navigation. "Check the pressure on Line 7" replaces a four-step manual workflow. The *Guide* was revolutionary because it let anyone ask a simple question and get a useful answer about any planet in the galaxy. This agent does the same thing for your device fleet -- except the answers are more accurate and the editorial stance is less opinionated.

### Secure by Default

Every request is authenticated through Cognito. Gateway validates JWTs before any tool call reaches Lambda. Runtime provides microVM isolation between operator sessions. No credentials are embedded in agent code.

### Real AWS Integration

Every tool call flows through real infrastructure: Gateway routes to Lambda, Lambda queries DynamoDB, Cognito issues and validates tokens. There are no simulated responses or mock services anywhere in the stack.

### Extensible Tool Surface

Adding a new device management capability means writing a Lambda handler and registering a tool schema with Gateway. The agent discovers new tools automatically through semantic search. No agent code changes required.

### Consumption-Based Cost

Runtime charges only for CPU time during active agent reasoning. While the agent waits for Lambda responses or model inference, I/O wait is free. For IoT operations that are often bursty -- quiet most of the time with spikes during shift changes or incidents -- this model is significantly cheaper than always-on infrastructure.

## Pricing

- **Runtime**: CPU consumption only (I/O wait while calling Lambda and model is free)
- **Gateway**: Per MCP tool call
- **Lambda**: Standard AWS Lambda pricing per invocation
- **DynamoDB**: Standard read/write capacity pricing
- **Cognito**: Per monthly active user
- **Bedrock**: Per-token pricing for Claude model calls
- **Free tier**: $200 for new AgentCore customers

## Troubleshooting

**Issue: Gateway returns AuthorizationError**
Solution: Verify the Cognito JWT is valid and not expired. Check that the `allowedAudiences` and `allowedClients` in the gateway configuration match the Cognito app client ID.

**Issue: Lambda times out on send_command**
Solution: Increase the Lambda timeout. If DynamoDB writes are slow, check the table's provisioned capacity and consider switching to on-demand capacity mode.

**Issue: list_devices returns empty results with location filter**
Solution: Verify the location string matches exactly. The GSI uses equality matching -- `factory-floor-1/line-7` will not match `factory-floor-1/line7`. Check the seeded data for the exact location format.

**Issue: Agent calls wrong tool**
Solution: Improve tool descriptions in the Gateway target schema. The model relies on these descriptions to select tools. Be specific about what each tool does and when to use it.

**Issue: send_command returns "device is offline"**
Solution: This is correct behavior. The Lambda handler checks device status before delivering commands. The agent should inform the operator and suggest checking the device's connectivity.

## Next Steps

Start with the three core tools (`get_device_status`, `list_devices`, `send_command`) and validate them against your real device fleet. Add telemetry history and IoT Core integration once the basic workflow is proven. Use Cedar policies to enforce command authorization, and add Memory to persist operator context across shifts so the morning crew knows what the night shift was investigating.

For fleets with thousands of devices, enable semantic search on the Gateway so the agent can efficiently discover the right tools across a growing set of device management capabilities.

The *Guide* has this to say about fleet management: "Space is big. Really big. You just won't believe how vastly, hugely, mind-bogglingly big it is." The same is true of IoT fleets. But with an agent that can talk to every device in your registry through natural language, the vastness becomes manageable. Your operators can stop memorizing cryptic device IDs and start asking plain questions. The devices, unlike Vogon ships, might even respond promptly.

**Documentation**: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/
**GitHub samples**: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

#AWS #AI #AgentCore #IoT #Gateway #Tutorial
