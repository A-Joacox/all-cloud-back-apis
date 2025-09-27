import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # S3 Configuration
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'cinema-data-bucket')
    S3_BACKUP_FOLDER = os.getenv('S3_BACKUP_FOLDER', 'backups')
    S3_ANALYTICS_FOLDER = os.getenv('S3_ANALYTICS_FOLDER', 'analytics')
    
    # DynamoDB Configuration
    DYNAMODB_TABLES = {
        'movies': os.getenv('DYNAMODB_MOVIES_TABLE', 'cinema-movies'),
        'rooms': os.getenv('DYNAMODB_ROOMS_TABLE', 'cinema-rooms'),
        'reservations': os.getenv('DYNAMODB_RESERVATIONS_TABLE', 'cinema-reservations'),
        'users': os.getenv('DYNAMODB_USERS_TABLE', 'cinema-users')
    }
    
    # RDS Configuration
    RDS_ENDPOINT = os.getenv('RDS_ENDPOINT')
    RDS_DATABASE = os.getenv('RDS_DATABASE', 'cinema_analytics')
    RDS_USER = os.getenv('RDS_USER', 'admin')
    RDS_PASSWORD = os.getenv('RDS_PASSWORD')
    RDS_PORT = int(os.getenv('RDS_PORT', 5432))
    
    # Local Database Configuration
    MYSQL_CONFIG = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', 'password'),
        'database': os.getenv('MYSQL_DATABASE', 'cinema_rooms')
    }
    
    POSTGRESQL_CONFIG = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'password'),
        'database': os.getenv('POSTGRES_DATABASE', 'cinema_reservations')
    }
    
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/cinema_movies')
    
    # Redis Configuration (for Celery)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Ingestion Settings
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 1000))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', 5))
    
    # Schedule Configuration
    BACKUP_SCHEDULE = os.getenv('BACKUP_SCHEDULE', '0 2 * * *')  # Daily at 2 AM
    SYNC_SCHEDULE = os.getenv('SYNC_SCHEDULE', '*/30 * * * *')   # Every 30 minutes
