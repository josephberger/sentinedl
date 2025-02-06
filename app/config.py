import os

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
