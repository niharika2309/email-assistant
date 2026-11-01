import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY", "none")
MODEL = os.getenv("MODEL", "Qwen3.8-Flash-Next")
