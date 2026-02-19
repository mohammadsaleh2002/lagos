import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'lagos-secret-key-change-in-production')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB = os.getenv('MONGO_DB', 'lagos')
    FERNET_KEY = os.getenv('FERNET_KEY', '')  # Generated on first run if empty

    # Color palette for article headings
    HEADING_COLORS = [
        '#1a73e8', '#e91e63', '#4caf50', '#ff9800', '#9c27b0',
        '#00bcd4', '#f44336', '#3f51b5', '#009688', '#ff5722',
        '#673ab7', '#2196f3', '#8bc34a', '#ffc107', '#795548',
    ]
