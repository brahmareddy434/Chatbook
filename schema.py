# To avoid confusion between the SQLAlchemy models and the Pydantic models, we will have the file models.py with the SQLAlchemy models, and the file schemas.py with the Pydantic models.

# These Pydantic models define more or less a "schema" (a valid data shape).

# So this will help us avoiding confusion while using both.


# create intial pydantic model / schemas


from pydantic import BaseModel,Field
from fastapi import Query

class Book(BaseModel):
    firstname: str
    lastname: str
    email :str
    password: str=Field(min_length=8)
    mobile_number:str
    age : int
    otp :str

    class Config:
        orm_mode = True
class Apiactivity(BaseModel):
    day:str
    date_and_time:str
    start_time: str
    end_time: str
    process_time :str
    method: str
    url:str
    headers : str
    query_params :str
    response_status_code:str

    class Config:
        orm_mode = True