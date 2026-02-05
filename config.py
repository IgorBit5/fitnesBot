import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
if not TOKEN:
    raise ValueError("Переменной BOT_TOKEN не найдено!")

if not API_KEY:
    raise ValueError("Переменной API_KEY не найдено!")