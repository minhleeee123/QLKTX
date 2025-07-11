# Makefile for QLKTX Client - Cross-platform version
# Automatically detects OS and uses appropriate commands

# Detect operating system
ifeq ($(OS),Windows_NT)
    detected_OS := Windows
    VENV_DIR := .venv
    PYTHON := $(VENV_DIR)\Scripts\python
    PIP := $(VENV_DIR)\Scripts\pip
    ACTIVATE := $(VENV_DIR)\Scripts\activate
    RM_DIR := rmdir /s /q
    MKDIR := mkdir
    EXISTS_CHECK := if exist
    NOT_EXISTS_CHECK := if not exist
else
    detected_OS := $(shell uname -s)
    VENV_DIR := .venv
    PYTHON := $(VENV_DIR)/bin/python
    PIP := $(VENV_DIR)/bin/pip
    ACTIVATE := source $(VENV_DIR)/bin/activate
    RM_DIR := rm -rf
    MKDIR := mkdir -p
    EXISTS_CHECK := test -d
    NOT_EXISTS_CHECK := test ! -d
endif

# Default target - show OS and run the app
all: show-os run

# Show detected OS
show-os:
	@echo "Detected OS: $(detected_OS)"

# Run the application
run:
ifeq ($(detected_OS),Windows)
	@$(PYTHON) application.py
else
	@$(PYTHON) application.py
endif

# Create virtual environment and install dependencies
install:
ifeq ($(detected_OS),Windows)
	@$(NOT_EXISTS_CHECK) $(VENV_DIR) python -m venv $(VENV_DIR)
	@$(PIP) install -r requirements.txt
	@echo Virtual environment created and dependencies installed for Windows
else
	@$(NOT_EXISTS_CHECK) $(VENV_DIR) && python3 -m venv $(VENV_DIR) || true
	@$(PIP) install -r requirements.txt
	@echo Virtual environment created and dependencies installed for $(detected_OS)
endif

# Install dependencies only (assuming venv exists)
deps:
	@$(PIP) install -r requirements.txt
	@echo Dependencies installed

# Upgrade dependencies
upgrade:
	@$(PIP) install --upgrade -r requirements.txt
	@echo Dependencies upgraded

# Clean virtual environment
clean:
ifeq ($(detected_OS),Windows)
	@$(EXISTS_CHECK) $(VENV_DIR) $(RM_DIR) $(VENV_DIR)
	@echo Virtual environment removed (Windows)
else
	@$(RM_DIR) $(VENV_DIR) 2>/dev/null || true
	@echo Virtual environment removed ($(detected_OS))
endif

# Reinstall everything (clean + install)
reinstall: clean install

# Show help
help:
	@echo "QLKTX Client Makefile - Detected OS: $(detected_OS)"
	@echo ""
	@echo "Available targets:"
	@echo "  all        - Show OS and run the application (default)"
	@echo "  run        - Run the application"
	@echo "  install    - Create venv and install dependencies"
	@echo "  deps       - Install/update dependencies only"
	@echo "  upgrade    - Upgrade all dependencies"
	@echo "  clean      - Remove virtual environment"
	@echo "  reinstall  - Clean and reinstall everything"
	@echo "  show-os    - Show detected operating system"
	@echo "  help       - Show this help message"

# Declare phony targets
.PHONY: all show-os run install deps upgrade clean reinstall help
