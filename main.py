import uvicorn
from fastapi import FastAPI,Request
from fastapi_sqlalchemy import DBSessionMiddleware, db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr,BaseModel
from typing import List
from fastapi.responses import JSONResponse,HTMLResponse
import random
import os,sys
from auth_beare import JWTBearer
from auth import signJWT
import webbrowser
import requests
from sqlalchemy.exc import IntegrityError





from schema import Book as SchemaBook
# from schema import Author as SchemaAuthor

from schema import Book
# from schema import Author
from passlib.context import CryptContext



# ########

from fastapi import FastAPI, Body, Depends

# from models import PostSchema, UserSchema, UserLoginSchema
from auth_beare import JWTBearer
from auth import signJWT

# from fastapi import FastAPI, Body

# from app.model import PostSchema, UserSchema, UserLoginSchema
# from app.auth.auth_handler import signJWT
# ########



from models import Book as ModelBook
# from models import Author as ModelAuthor

import os
from dotenv import load_dotenv

load_dotenv('.env')


app = FastAPI()

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



engine = create_engine(os.environ['DATABASE_URL'])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
dbs = SessionLocal()

# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


@app.get("/s")
async def root():
    html_content = """
    <html>
    <head>
        <title>HTML Response</title>
    </head>
    <body>
        <h1>Welcome to the Softsuave .... here you can change the password</h1>
        
        <form action="/forgot" method="post">
        <lable>OTP</lable><br><input type=text name="otp"><br><br>
        <lable>Email</lable><br><input type="text" name="email"><br><br>
        <lable>password</lable><br><input type="password" name="password"><br><br>
        <lable>Re Enter password</lable><br><input type="password" name="re_password"><br><br>
        <input type=submit value="Submit">
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)



@app.post('/register/', response_model=SchemaBook)
# changes in register 
async def post_book(book: SchemaBook):
    try:
        encrypt_pass=get_password_hash(book.password)
        db_book = ModelBook(firstname=book.firstname, lastname=book.lastname,email=book.email, password = encrypt_pass,mobile_number=book.mobile_number,age=book.age,token=book.token)
        db.session.add(db_book)
        db.session.commit()
        message = MessageSchema(
                   subject="Fastapi-Mail module",
                   recipients=[book.email],
                   body="Registration is successfully completed with user name  :"+book.email,
                   subtype=MessageType.html,
                )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
        message_for_frontend={
        "statusCode":200,
        "message": "Register Completed Successfully",
        "status":"Success",
        }       
        return JSONResponse(content=message_for_frontend,status_code=200)
    except Exception as e:
        
        return JSONResponse(content="Email Alredy Register Please Provide A New Email ", status_code=400)
           

@app.get("/auth/login/{email},{password}")
async def login(email:str,password:str):

    db_book = dbs.query(ModelBook).filter(ModelBook.email == email).first()
    if verify_password(password,db_book.password):
        message_for_frontend={
        "statusCode":200,
        "message": "Login Successfully",
        "status":"Success",
        "access token":signJWT(email),
        
        } 
        return JSONResponse(content=message_for_frontend,status_code=200)
    else:
        return "error wrong vaildate password"



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
    
@app.put("/change_password/{email},{password},{newpassword},{enter_new_password_again}",dependencies=[Depends(JWTBearer())])
async def changepassword(email:str,password:str,newpassword:str,enter_new_password_again):
    try:
        if len(newpassword) < 8:
            return JSONResponse(content="Password is too weak it should be more than 8 characters")
        db_books = dbs.query(ModelBook).filter(ModelBook.email == email).first()
        db_book = db.session.query(ModelBook).get(db_books.id)
        if verify_password(password,db_book.password):
            if newpassword==enter_new_password_again:
             
             if db_book:

                newpass=get_password_hash(newpassword)
                db_book.password=newpass
                db.session.commit()
                message_for_frontend={
                "statusCode":200,
                "message": "Password Changed Successfully",
                "status":"Success",
                }
                return JSONResponse(content=message_for_frontend,status_code=200)
    except IntegrityError as e:
        return JSONResponse(content="Check Credentials ", status_code=400)
    # 

    except Exception as e:
        
        return JSONResponse(content=str(e), status_code=400)
    
@app.post("/forgotpassword")
async def send_with_template(email_input: str):
    random_number = random.randint(1000, 9999)

    try:
      db_books = dbs.query(ModelBook).filter(ModelBook.email == email_input).first()
      db_book = db.session.query(ModelBook).get(db_books.id)
      db_book.token=random_number
      db.session.commit()    
    except Exception as e:
        return JSONResponse(content="Email is not Registered as a valid User ",status_code=400)
    
    
    Li=[email_input]
    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=Li,
        body="Your otp for forget password is "+str(random_number)+ "<br> this otp will expire in 5 minutes",
        subtype=MessageType.html,
        )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email_template.html") 
    webbrowser.open_new_tab("http://127.0.0.1:8000/s")
    return JSONResponse(status_code=200, content={"message": "Email has been sent successfully. Another API will open in a new tab."})


@app.post("/forgot")
async def forgotpassword(request:Request):
    form_data = await request.form()
    email=form_data["email"]
    otp = form_data["otp"]
    password = form_data["password"]
    re_password = form_data["re_password"]
    db_books = dbs.query(ModelBook).filter(ModelBook.email == email).first()
    db_book = db.session.query(ModelBook).get(db_books.id)
    try:
        if len(password)<8:
            message_for_frontend={
        "statusCode":200,
        "message": "password should be more than 8 characters",
        "status":"Success",
        
        } 
            return JSONResponse(content=message_for_frontend,status_code=400)
        if otp == db_book.token and otp !="string":
            if password == re_password:
                if db_book:
                  newpass=get_password_hash(password)
                  db_book.password=newpass
                  db_book.token="string"
                  db.session.commit()
                  Li=[email]
                  message = MessageSchema(
                   subject="Fastapi-Mail module",
                   recipients=Li,
                   body="Your Passord changed successfully",
                   subtype=MessageType.html,
                )
                fm = FastMail(conf)
                await fm.send_message(message, template_name="email_template.html")
                message_for_frontend={
        "statusCode":200,
        "message": "password changed Successfully",
        "status":"Success",
        
        } 
                return JSONResponse(content=message_for_frontend,status_code=200)
            else:
              message_for_frontend={
        "statusCode":400,
        "message": "both password is mismatch...",
        "status":"Success",
        
        } 
              return JSONResponse(content=message_for_frontend,status_code=400)
    except Exception as e:
        message_for_frontend={
        "statusCode":400,
        "message": "credentials wrong...",
        "status":"fail",
        
        } 
        return JSONResponse(content=message_for_frontend,status_code=400)












