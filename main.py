from collections import UserString
import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware
from pydantic import schema_json_of

from sqlalchemy.orm import Session

import models  # Remove the dot (.) before "import models"

from database import SessionLocal, engine
load_dotenv('.env')
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=os.getenv('DATABASE_URI'))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def getItems(session: Session = Depends(get_db)):  # Update "get_session" to "get_db"
    users = session.query(models.User).all()
    if users :
        return users
    return "Nothing is in db"
# @app.post("/postsomething/{username}")
# def postSomething(session: Session , username:str):
#     new_user = models.User(username=username)
#     session.add(new_user)
#     session.commit()
#     return new_user
