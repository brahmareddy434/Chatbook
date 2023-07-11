import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db

from schema import Book as SchemaBook
# from schema import Author as SchemaAuthor

from schema import Book
# from schema import Author
from passlib.context import CryptContext



from models import Book as ModelBook
# from models import Author as ModelAuthor

import os
from dotenv import load_dotenv

load_dotenv('.env')


app = FastAPI()

# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


@app.get("/")
async def root():
    return {"message": "hello world"}


@app.post('/register/', response_model=SchemaBook)
async def post_book(book: SchemaBook):
    encrypt_pass=get_password_hash(book.password)
    db_book = ModelBook(firstname=book.firstname, lastname=book.lastname,email=book.email, password = encrypt_pass,mobile_number=book.mobile_number,age=book.age)
    db.session.add(db_book)
    db.session.commit()
    return db_book

@app.get('/fetch_data/')
async def get_book():
    book = db.session.query(ModelBook).all()
    return book

@app.put('/update_user/{user_id}',response_model=SchemaBook)
async def update_book(user_id:int, book:SchemaBook):
    db_book = db.session.query(ModelBook).get(user_id)
    if db_book:
        db_book.firstname = book.firstname
        db_book.lastname = book.lastname
        db_book.email = book.email
        db_book.password = book.password
        db_book.mobile_number = book.mobile_number
        db_book.age = book.age
        db.session.commit()
        return db_book
    else:

        return "id not found pls provide a correct id"
    
@app.delete("/delete_user/{user_id}")
async def delete_user(user_id:int):
    db_book = db.session.query(ModelBook).get(user_id)

    if db_book:
        db.session.delete(db_book)
        db.session.commit()
        return db_book
    else:
        return"id not found pls provide a correct id"
    
@app.get("/login/{password},{id}")
async def login(password:str,id:int):
    db_book = db.session.query(ModelBook).get(id)
    if verify_password(password,db_book.password):
        return "login successfull welcome mr."+db_book.firstname+" "+db_book.lastname
    else:
        return "The password you entered is incorrect"




