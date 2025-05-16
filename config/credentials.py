from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env file in root

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
IS_PAPER = os.getenv("IS_PAPER", "true").lower() == "true"
