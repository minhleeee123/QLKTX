# Makefile for QLKTX Server - Simple version
# Just type "make" to run the app

# Default target - just run the app
all:
	@.venv\Scripts\python application.py

# Create venv if not exists
install:
	@if not exist .venv python -m venv .venv
	@.venv\Scripts\pip install -r requirements.txt

# Seed database with sample data
seed:
	@.venv\Scripts\python seed_db.py

# Clean venv
clean:
	@if exist .venv rmdir /s /q .venv
