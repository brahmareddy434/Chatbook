from fastapi import FastAPI,Request,status,HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware, db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr,BaseModel
from typing import List
from fastapi.responses import JSONResponse
import random
import os
from sqlalchemy.exc import IntegrityError
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from schema import Book as SchemaBook
from schema import Book
from passlib.context import CryptContext
from pydanticmodel import ChangePasswordRequest, LoginRequest,Forgotchangepassword
from fastapi import FastAPI, Body, Depends
from http.client import HTTPException
from models import Book as ModelBook
import os
from dotenv import load_dotenv
# from jwt.exceptions import InvalidSignatureError

load_dotenv('.env')


app = FastAPI(debug=True)


class EmailSchema(BaseModel):
    email: List[EmailStr]
class Settings(BaseModel):
   authjwt_secret_key: str = "secret"

@AuthJWT.load_config
def get_config():
    return Settings()

conf = ConnectionConfig(
    MAIL_USERNAME = os.environ["MAIL_USERNAME"],
    MAIL_PASSWORD = os.environ["MAIL_PASSWORD"],
    MAIL_FROM = os.environ["MAIL_FROM"],
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


@app.get("/")
async def root():
    message_for_frontend = {
        "status_code":200,
        "msg":"Welcome to Softsuave Technologies private limited...."
    }
    return JSONResponse(content=message_for_frontend,status_code=status.HTTP_200_OK)
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


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
        "message": "Register Completed Successfully",
        "status":"success"
        }       
        return JSONResponse(content=message_for_frontend,status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"msg":"email is already registered..","status":"Fail"}, status_code=400)
           
@app.post('/login')
async def login_page(user:LoginRequest,Authorize: AuthJWT = Depends()):
    
        user_id = dbs.query(ModelBook).filter(ModelBook.email == user.email).first()   
        if user_id and verify_password(user.password,user_id.password):
            access_token = Authorize.create_access_token(subject=user.email,fresh=True)
            refresh_token = Authorize.create_refresh_token(subject=user.email)
            message_for_frontend = {
                      "msg": "login successful mr." + user_id.firstname + " " + user_id.lastname,
                      "status":"success",
                      "tokens": {"access_token": access_token, "refresh_token": refresh_token}
                    }
            return JSONResponse(content=message_for_frontend, status_code=status.HTTP_200_OK)
        else:
            message={
                "msg":"entered credentials is incorrect",
                "status":"error",
            }
            return JSONResponse(content=message,status_code=status.HTTP_401_UNAUTHORIZED)
    
    
    # return {"access_token": access_token} 


# @app.get('/fetch_data/')
# async def get_book():
#     book = db.session.query(ModelBook).all()
#     return book

# @app.put('/update_user/{user_id}',response_model=SchemaBook)
# async def update_book(user_id:int, book:SchemaBook):
#     db_book = db.session.query(ModelBook).get(user_id)
#     if db_book:
#         db_book.firstname = book.firstname
#         db_book.lastname = book.lastname
#         db_book.email = book.email
#         db_book.password = book.password
#         db_book.mobile_number = book.mobile_number
#         db_book.age = book.age
#         db.session.commit()
#         return db_book
#     else:

#         return "id not found pls provide a correct id"
    
# @app.delete("/delete_user/{user_id}")
# async def delete_user(user_id:int):
#     db_book = db.session.query(ModelBook).get(user_id)

#     if db_book:
#         db.session.delete(db_book)
#         db.session.commit()
#         return db_book
#     else:
#         return"id not found pls provide a correct id"
    
@app.get('/change_password')
def decode_access_token(user:ChangePasswordRequest,Authorize: AuthJWT = Depends()):
    try:
        Authorize.fresh_jwt_required()
        
        decoded_token = Authorize.get_raw_jwt()
        user_email = decoded_token['sub']
        if len(user.new_password) < 8:
            return JSONResponse(content="Password is too weak it should be more than 8 characters",status_code=status.HTTP_400_BAD_REQUEST)
        db_books = dbs.query(ModelBook).filter(ModelBook.email == user_email).first()
        db_book = db.session.query(ModelBook).get(db_books.id)
        if verify_password(user.password,db_book.password):
            if user.new_password==user.confirm_password:
             
             if db_book:

                newpass=get_password_hash(user.new_password)
                db_book.password=newpass
                db.session.commit()
                message_for_frontend={
                
                "message": "Password Changed Successfully",
                "status":"Success",
                }
                return JSONResponse(content=message_for_frontend,status_code=status.HTTP_200_OK)
             
        else :
            return JSONResponse(content="Incorrect Password",status_code=status.HTTP_400_BAD_REQUEST) 
    except IntegrityError as e:
        return JSONResponse(content="Check Credentials ", status_code=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        
        return JSONResponse(content={'status_code':status.HTTP_400_BAD_REQUEST, 'message':e.message}, status_code=status.HTTP_400_BAD_REQUEST)
    
    # except  as e:
    #     return JSONResponse(content="Invalid Token",status_code=status.HTTP_400_BAD_REQUEST )

@app.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    """
    The jwt_refresh_token_required() function insures a valid refresh
    token is present in the request before running any code below that function.
    we can use the get_jwt_subject() function to get the subject of the refresh
    token, and use the create_access_token() function again to make a new access token
    """
    Authorize.jwt_refresh_token_required()
    

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user,fresh=True)
    
    return {"access_token": new_access_token,"status_code":status.HTTP_200_OK}
    
@app.post("/forgotpassword")
async def send_with_template(email_input: str):
    random_number = random.randint(1000, 9999)

    try:
      db_books = dbs.query(ModelBook).filter(ModelBook.email == email_input).first()
      db_book = db.session.query(ModelBook).get(db_books.id)
      db_book.token=random_number
      db.session.commit()    
    except Exception as e:
        message_for_frontend={
            "statusCode":400,
            "message":"unable to fetch the details of user check user name ...",
            "status":"Fail"
        }
        return JSONResponse(content="Email is not Registered as a valid User ",status_code=status.HTTP_400_BAD_REQUEST)
    
    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=[email_input],
        body="Your otp for forget password is "+str(random_number)+ "<br> this otp will expire in 5 minutes",
        subtype=MessageType.html,
        )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email_template.html") 
    return JSONResponse(status_code=200, content={"status_code":status.HTTP_200_OK,"message": "Email has been sent successfully."})


@app.post("/forgotchangepassword")
async def forgotpassword(details : Forgotchangepassword):
    try:
        if details.otp !="string":
            dbbook=dbs.query(ModelBook).filter(ModelBook.token == str(details.otp)).first()
            db_book = db.session.query(ModelBook).get(dbbook.id)
    except Exception as e:
        message_For_front_end={
            "statuscode":400,
            "message":"Invalid otp",
        }
        return JSONResponse(content=message_For_front_end,status_code=status.HTTP_400_BAD_REQUEST)
    
    if len(details.new_password) < 8:
        message_For_Front_end={
            "statuscode":400,
            "message":"password not reached the requirements is should be morethan 7 characters"
        }
        return JSONResponse(content=message_For_Front_end,status_code=status.HTTP_400_BAD_REQUEST)
    if details.new_password == details.confirm_password:
        newpass=get_password_hash(details.new_password)
        db_book.password=newpass
        db_book.token="string"
        db.session.commit()
        message = MessageSchema(
                   subject="Fastapi-Mail module",
                   recipients=[dbbook.email],
                   body="Your Passord changed successfully",
                   subtype=MessageType.html,
                  )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
        message_for_frontend={
                        "statusCode":200,
                        "message": "password changed Successfully",
                        "status":"Success",}                
        return JSONResponse(content=message_for_frontend,status_code=status.HTTP_200_OK)       
               
            
    else:
        message_for_frontend={
                   "statusCode":400,
                   "message": "both password is mismatch...",
                   "status":"Fail",} 
        return JSONResponse(content=message_for_frontend,status_code=status.HTTP_400_BAD_REQUEST)











