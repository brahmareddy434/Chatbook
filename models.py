# SQLAlchemy uses the term "model" to refer to these classes and instances that interact with the database.
 
# But Pydantic also uses the term "model" to refer to something different, the data validation, conversion, and documentation classes and instances.

# ********************************************************************************************************************************************************************************************************************************************************************

# import Base from database.py 
# create a classes that inherit from itertools

# ********************************************************************************************************************************************************************************************************************************************************************


# These classes are the SQLAlchemy models.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from json import JSONDecodeError
from json.decoder import JSONDecodeError


Base  = declarative_base()

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# from database import Base
# in the above line we are import the Base from the DB as mention in the above 

# Ok here after create some classes 


class Book(Base):
    __tablename__ = 'tabUsers'
    # this above line we are creating a table with the name of 'user', if we didn't mention the name it will take a name 

    id = Column(Integer,primary_key=True)

    firstname = Column(String)
    lastname = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    mobile_number= Column(String)
    age = Column(Integer)
    otp = Column(String)
    


# To avoid confusion between the SQLAlchemy models and the Pydantic models, we will have the file models.py with the SQLAlchemy models, and the file schemas.py with the Pydantic models.
# 
# These Pydantic models define more or less a "schema" (a valid data shape).
# 
# So this will help us avoiding confusion while using both.

class Apiactivity(Base):
    __tablename__ = 'tabActivity'
    id = Column(Integer, primary_key=True)
    day = Column(String)  # Change day to String
    date_and_time = Column(String)  # Change date_and_time to String
    start_time = Column(String)
    end_time = Column(String)
    process_time = Column(String)
    method = Column(String)
    url = Column(String)
    headers = Column(String)
    query_params = Column(String)
    response_status_code = Column(String)