# Makefile for Clover API Batch/Closeout Script
# Usage: make <target>

# Default Python interpreter
PYTHON := python3

# Default test parameters
TEST_YEAR := 2025
TEST_MONTH := 8

# Default virtual environment path
VENV := .venv

.PHONY: help clean test test-multi install setup venv activate requirements lint format check-config

# Default target
help:
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  clean        - Remove generated CSV files"
	@echo "  clean-all    - Remove CSV files and Python cache"
	@echo "  test         - Run test with default parameters (year=$(TEST_YEAR), month=$(TEST_MONTH))"
	@echo "  test-multi   - Run test with multiple months"
	@echo "  test-prev    - Run test for previous month"
	@echo "  install      - Install required packages"
	@echo "  setup        - Set up virtual environment and install packages"
	@echo "  venv         - Create virtual environment"
	@echo "  requirements - Generate/update requirements.txt"
	@echo "  check-config - Check if config.py exists"
	@echo "  run          - Run with custom parameters (use YEAR=... MONTH=... make run)"
	@echo ""
	@echo "Examples:"
	@echo "  make test"
	@echo "  make test YEAR=2024 MONTH=12"
	@echo "  make test-multi"
	@echo "  make clean"
	@echo "  make setup"

# Clean generated CSV files
clean:
	@echo "Removing CSV files..."
	rm -f *.csv
	@echo "CSV files removed."

# Clean CSV files and Python cache
clean-all: clean
	@echo "Removing Python cache files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Python cache files removed."

# Test with default parameters
test: check-config
	@echo "Running test with year=$(TEST_YEAR), month=$(TEST_MONTH)..."
	$(VENV)/bin/python clover.py --year $(TEST_YEAR) --month $(TEST_MONTH)

# Test with multiple months
test-multi: check-config
	@echo "Running test with multiple months (6,7,8)..."
	$(VENV)/bin/python clover.py --year $(TEST_YEAR) --month "6,7,8"

# Test with previous month (default behavior)
test-prev: check-config
	@echo "Running test for previous month..."
	$(VENV)/bin/python clover.py

# Run with custom parameters (use YEAR=... MONTH=... make run)
run: check-config
	@if [ -z "$(YEAR)" ] || [ -z "$(MONTH)" ]; then \
		echo "Usage: make run YEAR=2025 MONTH=8"; \
		echo "   or: make run YEAR=2025 MONTH=\"6,7,8\" for multiple months"; \
		exit 1; \
	fi
	@echo "Running with year=$(YEAR), month=$(MONTH)..."
	$(VENV)/bin/python clover.py --year $(YEAR) --month $(MONTH)

# Create virtual environment
venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV); \
		echo "Virtual environment created at $(VENV)"; \
	else \
		echo "Virtual environment already exists at $(VENV)"; \
	fi

# Install required packages
install: venv
	@echo "Installing required packages..."
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	@echo "Packages installed successfully."

# Full setup: create venv and install packages
setup: venv install
	@echo "Setup completed!"
	@echo "To activate the virtual environment, run:"
	@echo "  source $(VENV)/bin/activate"

# Generate/update requirements.txt from current environment
requirements:
	@if [ -d "$(VENV)" ]; then \
		echo "Generating requirements.txt from virtual environment..."; \
		$(VENV)/bin/pip freeze > requirements.txt; \
		echo "requirements.txt updated."; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Check if config.py exists
check-config:
	@if [ ! -f "config.py" ]; then \
		echo "WARNING: config.py not found!"; \
		echo "Please copy config_template.py to config.py and fill in your credentials:"; \
		echo "  cp config_template.py config.py"; \
		echo "  # Then edit config.py with your actual Clover API credentials"; \
		echo ""; \
		echo "Alternatively, you can use environment variables or command-line arguments."; \
		echo "See README.md for more information."; \
		exit 1; \
	fi

# Show help for custom test commands
test-help:
	@echo "Test command examples:"
	@echo "  make test                    - Test with default params ($(TEST_YEAR)/$(TEST_MONTH))"
	@echo "  make test YEAR=2024 MONTH=12 - Test with custom single month"
	@echo "  make test-multi              - Test with multiple months (6,7,8)"
	@echo "  make test-prev               - Test with previous month"
	@echo "  make run YEAR=2025 MONTH=9   - Run with specific parameters"
	@echo "  make run YEAR=2025 MONTH=\"1,2,3\" - Run with multiple months"

# Development targets
dev-test: check-config
	@echo "Running development test (verbose output)..."
	$(VENV)/bin/python clover.py --year $(TEST_YEAR) --month $(TEST_MONTH) --output "dev_test_output.csv"

# Show current configuration
show-config:
	@echo "Current configuration:"
	@echo "  Python: $(PYTHON)"
	@echo "  Virtual env: $(VENV)"
	@echo "  Test year: $(TEST_YEAR)"
	@echo "  Test month: $(TEST_MONTH)"
	@if [ -f "config.py" ]; then \
		echo "  Config file: ✓ config.py exists"; \
	else \
		echo "  Config file: ✗ config.py missing"; \
	fi
	@if [ -d "$(VENV)" ]; then \
		echo "  Virtual env: ✓ $(VENV) exists"; \
	else \
		echo "  Virtual env: ✗ $(VENV) missing"; \
	fi
