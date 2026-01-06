"""Configuration module for database and application settings."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class."""
    
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'fortalecimiento')
    DB_USER = os.getenv('DB_USER', '')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Excel file configuration
    EXCEL_FILE_PATH = os.getenv('EXCEL_FILE_PATH', 'data/beneficiarios.xlsx')
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/migration.log')
    
    @classmethod
    def get_database_url(cls):
        """Get the database connection URL."""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def validate(cls):
        """Validate required configuration parameters."""
        required = ['DB_USER', 'DB_PASSWORD', 'DB_NAME']
        missing = []
        
        for param in required:
            if not getattr(cls, param):
                missing.append(param)
        
        if missing:
            raise ValueError(f"Missing required configuration parameters: {', '.join(missing)}")
        
        return True
