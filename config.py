import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY', 'cd1b0a234fmsh446fc85989fa7c9p100226jsnc5d1f2a34053')
    API_FOOTBALL_HOST = 'api-football-v1.p.rapidapi.com'
    API_FOOTBALL_URL = 'https://api-football-v1.p.rapidapi.com/v3'
