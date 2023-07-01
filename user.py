from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app =FastAPI()

class User(BaseModel):
    first_name :str
    last_name :str
    email :str
    password :str

@app.post("/")
async def registration(user:User):
    return "Welcome mr/ms "+user.first_name+" "+user.last_name