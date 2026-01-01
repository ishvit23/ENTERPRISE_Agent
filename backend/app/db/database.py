"""
Database connection and session management for PostgreSQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.config import Config

config = Config('.env')
POSTGRES_USER = config('POSTGRES_USER', cast=str, default='postgres')
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD', cast=str, default='postgres')
POSTGRES_DB = config('POSTGRES_DB', cast=str, default='enterprise_assistant')
POSTGRES_HOST = config('POSTGRES_HOST', cast=str, default='db')
POSTGRES_PORT = config('POSTGRES_PORT', cast=str, default='5432')

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI to get DB session
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
