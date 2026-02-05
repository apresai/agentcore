# =============================================================================
# AgentCore Demo Test Framework
# "Time is an illusion. Lunchtime doubly so."
# =============================================================================

.PHONY: test test-quick test-medium test-slow test-hhgttg test-parallel \
        test-code-interpreter test-gateway test-browser test-runtime \
        test-memory test-comparison setup validate clean help

PYTHON  := python3
PYTEST  := $(PYTHON) -m pytest
TESTS   := tests

.DEFAULT_GOAL := help

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

setup: ## Install test dependencies
	@echo "Installing test dependencies..."
	pip install -r requirements-test.txt
	@echo "Done."

validate: ## Validate AWS credentials
	@echo "Validating AWS credentials..."
	@aws sts get-caller-identity --query 'Account' --output text || \
		(echo "ERROR: AWS credentials not configured. Run 'aws configure'." && exit 1)
	@echo "Region: $${AWS_REGION:-us-east-1}"
	@echo "Credentials OK."

# ---------------------------------------------------------------------------
# Test Suites
# ---------------------------------------------------------------------------

test: validate ## Run ALL integration tests (~20 min)
	@echo ""
	@echo "DON'T PANIC - Running all demos against real AWS."
	@echo "This may take 15-20 minutes. Grab a Pan Galactic Gargle Blaster."
	@echo ""
	$(PYTEST) $(TESTS)/integration/ -v --timeout=720

test-quick: validate ## Run fast tests only (~2 min)
	@echo "Running fast demos (runtime, code-interpreter, comparison)..."
	$(PYTEST) $(TESTS)/integration/ -v -m fast --timeout=180

test-medium: validate ## Run medium tests (~5 min)
	@echo "Running medium demos (gateway, browser)..."
	$(PYTEST) $(TESTS)/integration/ -v -m medium --timeout=360

test-slow: validate ## Run slow tests (~10 min)
	@echo "Running slow demos (memory)..."
	@echo "\"The first ten million years were the worst.\" - Marvin"
	$(PYTEST) $(TESTS)/integration/ -v -m slow --timeout=720

test-hhgttg: ## Run HHGTTG theme tests (no AWS needed)
	@echo "The Answer is 42."
	$(PYTEST) $(TESTS)/integration/ -v -m hhgttg --timeout=10

# ---------------------------------------------------------------------------
# Individual Demos
# ---------------------------------------------------------------------------

test-runtime: validate ## Runtime demo (~30s)
	@echo "Testing Deep Thought (Runtime)..."
	$(PYTEST) $(TESTS)/integration/test_runtime.py -v --timeout=180

test-code-interpreter: validate ## Code Interpreter demo (~15s)
	@echo "Testing Deep Thought's Calculator (Code Interpreter)..."
	$(PYTEST) $(TESTS)/integration/test_code_interpreter.py -v --timeout=180

test-comparison: validate ## Framework comparison demo (~1 min)
	@echo "Testing Multiple Perspectives (Comparison)..."
	$(PYTEST) $(TESTS)/integration/test_comparison.py -v --timeout=300

test-gateway: validate ## Gateway demo (~2 min)
	@echo "Testing The Babel Fish (Gateway)..."
	$(PYTEST) $(TESTS)/integration/test_gateway.py -v --timeout=360

test-browser: validate ## Browser demo (~2 min)
	@echo "Testing The Guide (Browser)..."
	$(PYTEST) $(TESTS)/integration/test_browser.py -v --timeout=360

test-memory: validate ## Memory demo (~10 min)
	@echo "Testing Marvin's Memory (Memory)..."
	@echo "\"Here I am, brain the size of a planet...\""
	$(PYTEST) $(TESTS)/integration/test_memory.py -v --timeout=720

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

clean: ## Remove test artifacts
	rm -rf .pytest_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

help: ## Show this help
	@echo ""
	@echo "AgentCore Demo Tests"
	@echo "\"Don't Panic\" - The Hitchhiker's Guide to the Galaxy"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-24s %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make setup          # First-time install"
	@echo "  make test-quick     # Fast demos only (~2 min)"
	@echo "  make test-runtime   # Just the Runtime demo"
	@echo "  make test           # Everything (~20 min)"
	@echo ""
