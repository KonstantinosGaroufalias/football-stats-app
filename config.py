import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY', 'xd')
    API_FOOTBALL_HOST = 'api-football-v1.p.rapidapi.com'
    API_FOOTBALL_URL = 'https://api-football-v1.p.rapidapi.com/v3'
