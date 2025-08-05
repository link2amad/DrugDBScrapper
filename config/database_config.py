import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    # Database connection settings
    SERVER = os.getenv('DB_SERVER', 'localhost')
    DATABASE = os.getenv('DB_NAME', 'MedicineDatabase')
    USERNAME = os.getenv('DB_USERNAME', 'sa')
    PASSWORD = os.getenv('DB_PASSWORD', '')
    DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    # Connection string
    @classmethod
    def get_connection_string(cls):
        return (
            f"DRIVER={{{cls.DRIVER}}};"
            f"SERVER={cls.SERVER};"
            f"DATABASE={cls.DATABASE};"
            f"UID={cls.USERNAME};"
            f"PWD={cls.PASSWORD};"
            "Trusted_Connection=yes;"
        )
    
    # Alternative connection string for Windows Authentication
    @classmethod
    def get_trusted_connection_string(cls):
        return (
            f"DRIVER={{{cls.DRIVER}}};"
            f"SERVER={cls.SERVER};"
            f"DATABASE={cls.DATABASE};"
            "Trusted_Connection=yes;"
        ) 