import os
from dotenv import load_dotenv
load_dotenv()

appKey= os.getenv('appKey')
SPOTIPY_CLIENT_ID= os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET=os.getenv('SPOTIPY_CLIENT_SECRET')
