# SQLAlchemy uses the term "model" to refer to these classes and instances that interact with the database.
 
# But Pydantic also uses the term "model" to refer to something different, the data validation, conversion, and documentation classes and instances.

# ********************************************************************************************************************************************************************************************************************************************************************

# import Base from database.py 
# create a classes that inherit from itertools

# ********************************************************************************************************************************************************************************************************************************************************************


# These classes are the SQLAlchemy models.

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from database import Base
# in the above line we are import the Base from the DB as mention in the above 

# Ok here after create some classes 


class User(Base):
    __tablename__ = 'tabUser'
    # this above line we are creating a table with the name of 'user', if we didn't mention the name it will take a name 

    id = Column(Integer,primary_key=True)

    firstname = Column(String)
    lastname = Column(String)
    email = Column(String)
    password = Column(String)



# To avoid confusion between the SQLAlchemy models and the Pydantic models, we will have the file models.py with the SQLAlchemy models, and the file schemas.py with the Pydantic models.
# 
# These Pydantic models define more or less a "schema" (a valid data shape).
# 
# So this will help us avoiding confusion while using both.

