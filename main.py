import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail,ConnectionConfig,MessageSchema,MessageType
from pydantic import EmailStr,BaseModel
from typing import List
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


class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME = "sharanm933@gmail.com",
    MAIL_PASSWORD = "mxmyzkeqzoipvour",
    MAIL_FROM = "sharanm933@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="Desired Name",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)


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
    try:
        encrypt_pass=get_password_hash(book.password)
        db_book = ModelBook(firstname=book.firstname, lastname=book.lastname,email=book.email, password = encrypt_pass,mobile_number=book.mobile_number,age=book.age)
        # unique_username=db.session.query(ModelBook).get(book.email)
        # if unique_username:
        #     return "email alredy registered"
        # else:
        db.session.add(db_book)
        db.session.commit()
        return db_book
    except Exception as e:
        
        return JSONResponse(content="Email Alredy Register Please Provide A New Email ", status_code=400)
           
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
    
@app.post("/email")
async def send_with_template(email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=email.dict().get("email"),
        template_body=email.dict().get("body"),
        subtype=MessageType.html,
        )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email_template.html") 
    return JSONResponse(status_code=200, content={"message": "email has been sent"})




