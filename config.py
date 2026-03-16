import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
BASE_URL = os.getenv("BASE_URL")
LOGIN_URL = os.getenv("LOGIN_URL")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"