import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Теперь получаем значения переменных
SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')