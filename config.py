import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_KEY = os.environ.get('RWGPS_API_KEY')

# Cache Configuration
CACHE_FILE = 'trips_cache.pkl'
CACHE_DURATION = 24 * 60 * 60  # 24 hours in seconds


TOKEN_FILE = os.path.expanduser('~/.rwgps/token')
TOKEN_DURATION = 24 * 60 * 60  # 24 hours in seconds

