"""Configuration module for the email sending system.

This module loads settings from environment variables or a .env file
and exposes them as variables. It complies with PEP 8 and Clean Code guidelines.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if it exists
load_dotenv(BASE_DIR / ".env")

# SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
try:
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
except ValueError:
    SMTP_PORT = 587

SMTP_USER = os.getenv("SMTP_USER", "dsofia0528@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() in ("true", "1", "yes")

# Simulation mode (True by default for safe local development/testing)
SMTP_SIMULATION = os.getenv("SMTP_SIMULATION", "True").lower() in ("true", "1", "yes")

# Directories for simulated output and logs
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
