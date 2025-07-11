# Makefile for QLKTX Server - Cross-platform version
# Automatically detects OS and uses appropriate commands

# Detect operating system
ifeq ($(OS),Windows_NT)
    detected_OS := Windows
    VENV_DIR := .venv
    PYTHON := $(VENV_DIR)\Scripts\python
    PIP := $(VENV_DIR)\Scripts\pip
    FLASK := $(VENV_DIR)\Scripts\flask
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
    FLASK := $(VENV_DIR)/bin/flask
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

# Run with Flask development server
dev:
ifeq ($(detected_OS),Windows)
	@set FLASK_ENV=development && $(PYTHON) application.py
else
	@FLASK_ENV=development $(PYTHON) application.py
endif

# Create virtual environment and install dependencies
install:
ifeq ($(detected_OS),Windows)
	@$(NOT_EXISTS_CHECK) $(VENV_DIR) python -m venv $(VENV_DIR)
	@$(PIP) install -r requirements.txt
	@echo "Virtual environment created and dependencies installed for Windows"
else
	@$(NOT_EXISTS_CHECK) $(VENV_DIR) && python3 -m venv $(VENV_DIR) || true
	@$(PIP) install -r requirements.txt
	@echo "Virtual environment created and dependencies installed for $(detected_OS)"
endif

# Install dependencies only (assuming venv exists)
deps:
	@$(PIP) install -r requirements.txt
	@echo Dependencies installed

# Upgrade dependencies
upgrade:
	@$(PIP) install --upgrade -r requirements.txt
	@echo Dependencies upgraded

# Initialize database schema
init-db:
	@$(PYTHON) -c "from app.extensions import db; from app import create_app; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized')"

# Seed database with sample data
seed:
	@$(PYTHON) seed_db.py
	@echo Database seeded with sample data

# Setup database (init + seed)
setup-db: init-db seed

# Reset database (drop all tables and recreate)
reset-db:
	@$(PYTHON) -c "from app.extensions import db; from app import create_app; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all(); print('Database reset')"

# Run database migrations (if using Flask-Migrate)
migrate:
ifeq ($(detected_OS),Windows)
	@$(FLASK) db upgrade
else
	@$(FLASK) db upgrade
endif

# Create new migration
migration:
ifeq ($(detected_OS),Windows)
	@$(FLASK) db migrate -m "$(msg)"
else
	@$(FLASK) db migrate -m "$(msg)"
endif

# Run tests (if you have tests)
test:
	@$(PYTHON) -m pytest tests/ -v || echo "No tests found or pytest not installed"

# Check code style with flake8
lint:
	@$(PIP) show flake8 > /dev/null 2>&1 && $(PYTHON) -m flake8 app/ || echo "flake8 not installed, skipping lint check"

# Format code with black
format:
	@$(PIP) show black > /dev/null 2>&1 && $(PYTHON) -m black app/ || echo "black not installed, skipping code formatting"

# Clean virtual environment
clean:
ifeq ($(detected_OS),Windows)
	@$(EXISTS_CHECK) $(VENV_DIR) $(RM_DIR) $(VENV_DIR)
	@echo "Virtual environment removed (Windows)"
else
	@$(RM_DIR) $(VENV_DIR) 2>/dev/null || true
	@echo "Virtual environment removed ($(detected_OS))"
endif

# Clean database files (SQLite)
clean-db:
ifeq ($(detected_OS),Windows)
	@if exist *.db del *.db
	@if exist instance rmdir /s /q instance
	@echo "Database files cleaned (Windows)"
else
	@rm -f *.db 2>/dev/null || true
	@rm -rf instance/ 2>/dev/null || true
	@echo "Database files cleaned ($(detected_OS))"
endif

# Clean everything (venv + db)
clean-all: clean clean-db

# Reinstall everything (clean + install)
reinstall: clean install

# Full setup (install + setup database)
setup: install setup-db

# Show help
help:
	@echo "QLKTX Server Makefile - Detected OS: $(detected_OS)"
	@echo ""
	@echo "Available targets:"
	@echo "  all        - Show OS and run the application (default)"
	@echo "  run        - Run the application"
	@echo "  dev        - Run in development mode"
	@echo "  install    - Create venv and install dependencies"
	@echo "  deps       - Install/update dependencies only"
	@echo "  upgrade    - Upgrade all dependencies"
	@echo ""
	@echo "Database targets:"
	@echo "  init-db    - Initialize database schema"
	@echo "  seed       - Seed database with sample data"
	@echo "  setup-db   - Initialize and seed database"
	@echo "  reset-db   - Drop and recreate all tables"
	@echo "  migrate    - Run database migrations"
	@echo "  migration  - Create new migration (use: make migration msg='description')"
	@echo ""
	@echo "Development targets:"
	@echo "  test       - Run tests"
	@echo "  lint       - Check code style"
	@echo "  format     - Format code with black"
	@echo ""
	@echo "Cleanup targets:"
	@echo "  clean      - Remove virtual environment"
	@echo "  clean-db   - Remove database files"
	@echo "  clean-all  - Remove venv and database files"
	@echo "  reinstall  - Clean and reinstall everything"
	@echo ""
	@echo "Setup targets:"
	@echo "  setup      - Full setup (install + setup-db)"
	@echo "  show-os    - Show detected operating system"
	@echo "  help       - Show this help message"

# Declare phony targets
.PHONY: all show-os run dev install deps upgrade init-db seed setup-db reset-db migrate migration test lint format clean clean-db clean-all reinstall setup help
