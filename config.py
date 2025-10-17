import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGO_URI = os.getenv('MONGO_URI')
    AI_SERVICE_BASE_URL = os.getenv('AI_SERVICE_BASE_URL', 'http://placeholder.com/api') 
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS = 3600