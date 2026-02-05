"""
Shared pytest fixtures for AgentCore demo tests.

"The Guide is definitive. Reality is frequently inaccurate."
"""

import os
import sys
import subprocess
import pytest
from pathlib import Path
from typing import Tuple

try:
    import boto3
except ImportError:
    boto3 = None

# Project paths
REPO_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = REPO_ROOT / "articles" / "examples"


# ---------------------------------------------------------------------------
# Session-scoped: validate AWS once before all tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def validate_aws_credentials(request):
    """Validate AWS credentials before running any integration tests."""
    # Skip AWS validation for hhgttg-only test runs
    markers = [mark.name for item in request.session.items for mark in item.iter_markers()]
    if all(m == "hhgttg" for m in markers if m in ("hhgttg", "integration")):
        return

    if boto3 is None:
        # boto3 not in test runner, but demos use their own venv -
        # validate credentials via CLI instead
        try:
            result = subprocess.run(
                ["aws", "sts", "get-caller-identity"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                pytest.skip(f"AWS credentials not configured: {result.stderr}")
            else:
                print(f"\n  AWS credentials validated via CLI")
                print(f"  Region: {os.getenv('AWS_REGION', 'us-east-1')}")
        except FileNotFoundError:
            pytest.skip("AWS CLI not installed - cannot validate credentials")
        return

    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        print(f"\n  AWS Account : {identity['Account']}")
        print(f"  AWS Identity: {identity['Arn']}")
        print(f"  Region      : {os.getenv('AWS_REGION', 'us-east-1')}")
    except Exception as e:
        pytest.skip(f"AWS credentials not configured: {e}")


@pytest.fixture(scope="session")
def aws_region() -> str:
    return os.getenv("AWS_REGION", "us-east-1")


# ---------------------------------------------------------------------------
# Demo runner fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def run_demo():
    """
    Fixture that returns a callable to run any demo by name.

    Usage inside a test:
        stdout, stderr, code = run_demo("runtime", timeout=120)
    """

    def _run(
        demo_name: str,
        timeout: int = 600,
        env_vars: dict | None = None,
    ) -> Tuple[str, str, int]:
        demo_dir = EXAMPLES_DIR / demo_name
        demo_script = demo_dir / "main.py"

        if not demo_script.exists():
            pytest.fail(f"Demo script not found: {demo_script}")

        # Use the demo's own venv if it exists, otherwise system python
        venv_python = demo_dir / "venv" / "bin" / "python"
        python = str(venv_python) if venv_python.exists() else sys.executable

        env = os.environ.copy()
        env.setdefault("AWS_REGION", "us-east-1")
        if env_vars:
            env.update(env_vars)

        result = subprocess.run(
            [python, str(demo_script)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(demo_dir),
            env=env,
        )

        return result.stdout, result.stderr, result.returncode

    return _run


# ---------------------------------------------------------------------------
# Helpers available to all tests
# ---------------------------------------------------------------------------

def assert_success(stdout: str, patterns: list[str]):
    """Assert every pattern appears in stdout."""
    for pat in patterns:
        assert pat in stdout, f"Missing expected output: {pat!r}"


def assert_no_errors(stdout: str, stderr: str, returncode: int):
    """Assert no error indicators in output."""
    assert returncode == 0, f"Exit code {returncode}\nstderr: {stderr}"
    assert "❌" not in stdout, "Error indicator (❌) found in stdout"
    # Allow stderr warnings (e.g. deprecation) as long as exit code is 0
