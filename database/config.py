import os
from dotenv import load_dotenv

load_dotenv() # This loads the variables from .env into the environment

class Config:
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT",27920))
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME", "defaultdb")
    DATABASE_URL =os.getenv("DB_Connection")