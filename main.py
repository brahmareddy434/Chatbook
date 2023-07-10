import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db

from schema import Book as SchemaBook
# from schema import Author as SchemaAuthor

from schema import Book
# from schema import Author

from models import Book as ModelBook
# from models import Author as ModelAuthor

import os
from dotenv import load_dotenv

load_dotenv('.env')


app = FastAPI()

# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])

@app.get("/")
async def root():
    return {"message": "hello world"}


@app.post('/create a user /', response_model=SchemaBook)
async def book(book: SchemaBook):
    db_book = ModelBook(firstname=book.firstname, lastname=book.lastname,email=book.email, password = book.password,mobile_number=book.mobile_number,age=book.age)
    db.session.add(db_book)
    db.session.commit()
    return db_book

@app.get('/book/')
async def book():
    book = db.session.query(ModelBook).all()
    return book




