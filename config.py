from datetime import timedelta

class Config:
    # Flask configuration
    SECRET_KEY = 'you-will-never-guess'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/records.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Application configuration
    APP_NAME = 'Banking App'
    ADMIN_EMAIL = 'admin@bankingapp.com'
    
    # Security configuration
    PASSWORD_RESET_EXPIRY = 3600  # 1 hour
    
    # Transaction limits
    MAX_TRANSACTION_AMOUNT = 10000
    DAILY_TRANSACTION_LIMIT = 25000
