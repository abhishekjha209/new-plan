import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. Retrieve the Database connection URL from environment variables
# If running inside Docker, 'db' is resolved automatically to the Postgres container
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/mydb")

# 2. Create the Database Engine
# The engine is the structural anchor that maintains a connection pool
engine = create_engine(
    DATABASE_URL,
    # pool_pre_ping=True checks the health of connection sockets before using them,
    # preventing errors if PostgreSQL drops a silent connection
    pool_pre_ping=True 
)

# 3. Create a SessionLocal class
# Each instance of SessionLocal will represent a database transaction / working session
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# 4. Define the Modern Declarative Base (SQLAlchemy 2.0 Style)
# All database models will inherit from this Base class to register with the mapper
class Base(DeclarativeBase):
    pass
