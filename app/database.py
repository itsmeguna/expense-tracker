from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker
import os

# PostgreSQL connection URL (adjust password/database name as needed)

#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:FF66fK0=@localhost:5432/FASTAPI"
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
print("Using DB URL:", SQLALCHEMY_DATABASE_URL)

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() 

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
