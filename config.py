# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASS')  # Rename to match your .env
ADMIN_EMAIL = EMAIL_USER
