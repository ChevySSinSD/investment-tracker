from sqlalchemy import create_engine
"""
This module sets up the SQLAlchemy database connection and ORM base for the investment tracker application.

Attributes:
    SQLALCHEMY_DATABASE_URL (str): The database URL for the SQLite database.
    engine (sqlalchemy.engine.Engine): The SQLAlchemy engine instance connected to the database.
    SessionLocal (sqlalchemy.orm.session.sessionmaker): Factory for creating new SQLAlchemy sessions.
    Base (sqlalchemy.orm.declarative_base): Base class for declarative class definitions.
"""
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/portfolio.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()