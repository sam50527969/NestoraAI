from dotenv import load_dotenv
import os

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Nestora AI Backend")
APP_ENV = os.getenv("APP_ENV", "development")