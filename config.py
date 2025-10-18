import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGO_URI = os.getenv('MONGO_URI')
    OPEN_API_KEY = os.getenv('OPEN_API_KEY') 
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS = 3600