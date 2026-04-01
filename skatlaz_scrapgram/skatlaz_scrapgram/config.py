import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "skatlaz_secret")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///scrapgram.db")
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "secret")
