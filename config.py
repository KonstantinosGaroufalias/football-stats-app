import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY', 'abc')
    API_FOOTBALL_HOST = 'api-football-v1.p.rapidapi.com'
    API_FOOTBALL_URL = 'https://api-football-v1.p.rapidapi.com/v3'
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///football_stats.db'

class DevelopmentConfig(Config):
    DEBUG = True