from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

sqlalchemy_database = "postgresql://postgres:postgres@127.0.0.1:5432/fastapi"

engine = create_engine(sqlalchemy_database)

SessionLocal = sessionmaker(bind=engine, autocommit=False)
Base = declarative_base()
#  now we will use the function declarative_base() that return a class



