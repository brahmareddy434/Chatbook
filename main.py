from fastapi import FastAPI,Request, logger,status,HTTPException,Path,Response
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
from pydanticmodel import ChangePasswordRequest, LoginRequest,Forgotchangepassword,Register
from fastapi import FastAPI, Body, Depends
from http.client import HTTPException
from models import Book as ModelBook
from models import Apiactivity 
import os
from json import JSONDecodeError
from datetime import datetime,timezone,timedelta
import time
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import db
from sqlalchemy.exc import IntegrityError


import logging
logging.config.fileConfig('logging_config.ini')
logging.basicConfig(level=logging.INFO)
load_dotenv('.env')

app = FastAPI(debug=True)

logging.config.fileConfig('logging_config.ini', disable_existing_loggers=False)

logger = logging.getLogger(__name__)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_history = []
@app.middleware("http")
async def add_name(request: Request, call_next):
   
        
       
    try:
        logger.info(f"start request path={request.url}")
        start_time = time.time()



        present_date=datetime.now()
        ind_time = timezone(timedelta(hours=5,minutes=30))
        current_dateandtime=present_date.astimezone(ind_time)
        start_time = time.time()
        dayy=current_dateandtime.strftime('%Y-%m-%d')
        timee=current_dateandtime.strftime("%H:%M:%S.%f")

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        formatted_process_time = '{0:.2f}'.format(process_time)
        logger.info(f"completed_in={formatted_process_time} ms")
        if response.status_code == 422:
            content={"message":"Required fields are missing"}
            logger.error(f"{content}, status_code={status.HTTP_422_UNPROCESSABLE_ENTITY}")

            return JSONResponse(content={"message":"Required fields are missing","status":"Fail"},status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        end_time = time.time()
        process_time = end_time - start_time
        api_activity = Apiactivity(
            date=str(datetime.now())[:10],
            time=str(datetime.now())[11:],
            start_time=str(start_time),
            end_time=str(end_time),
            process_time=str(process_time),
            method=request.method,
            url=str(request.url),
            headers=str(dict(request.headers)),
            query_params=str(dict(request.query_params)),
            response_status_code=str(response.status_code),
        )
        db.session.add(api_activity)
        db.session.commit()
        api_history.append(1)
        logger.info(f"response={response},request_path={request.url}")
        return response
    except JSONDecodeError:
        logger.error(f"msg={content},status={status.HTTP_400_BAD_REQUEST},request_path={request.url}")
        return JSONResponse(
            content={"message": "Invalid JSON data in request body"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        logger.error(f"msg={content},status={status.HTTP_400_BAD_REQUEST},request_path={request.url}")
        return JSONResponse(
            content={"message": str(e), "status": "Fail"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )


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
async def root(request:Request):
    message_for_frontend = {
        "status_code":200,
        "msg":"Welcome to Softsuave Technologies private limited...."
    }
    logger.info(f"{message_for_frontend}, status_code={status.HTTP_200_OK},request_path={request.url}")
    return JSONResponse(content=message_for_frontend,status_code=status.HTTP_200_OK)
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.post('/register/', response_model=SchemaBook)
async def post_book(book: Register,request: Request):
    
    if len(list(book)) != 6:
        message_for_frontend = {"message":"Required fields are missing...","status":"Fail"}
        logger.info(f"{message_for_frontend}, request_path={request.url},status_code={status.HTTP_422_UNPROCESSABLE_ENTITY}")
        return JSONResponse(content=message_for_frontend,status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    try:
        encrypt_pass=get_password_hash(book.password)
        db_book = ModelBook(firstname=book.firstname, lastname=book.lastname,email=book.email, password = encrypt_pass,mobile_number=book.mobile_number,age=book.age,otp="string")
        emailstr=db_book.email
        if '@' and '.com' in emailstr:
            pass
        else:
            message_for_frontend={
        "message": "Invalid email Type",
        "status":"Fail"
        }
            logger.warning(f"message{message_for_frontend},request_path={request.url},status_code={status.HTTP_400_BAD_REQUEST}")
            return JSONResponse(content=message_for_frontend ,request_path={request.url.path},status_code=status.HTTP_400_BAD_REQUEST)
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
        logger.info(f"msg={message_for_frontend}, request_path={request.url},status_code={status.HTTP_200_OK}")
    
        return JSONResponse(content=message_for_frontend, status_code=status.HTTP_200_OK)
    except HTTPException as e:
        if e.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            # logger.error(" Required fields are missing,{request.url}")
            logger.error(f"msg={message_for_frontend}, request_path={request.url},status_code={status.HTTP_400_BAD_REQUEST}")
            return JSONResponse(content={"msg": "Required fields are missing.", "status": "Fail"}, status_code=status.HTTP_400_BAD_REQUEST)
        else:
            logger.info(f"msg={e.detail}, request_path={request.url},status_code={status.e.status_code}")
            return JSONResponse(content={"msg": e.detail, "status": "Fail"}, status_code=e.status_code)
    
    except Exception as IntegrityError:
        logger.error(f"msg= Email Already Register , status_code={status.HTTP_400_BAD_REQUEST}, request_path={request.url}")

        return JSONResponse(content={"msg": str(e), "status": "Fail"}, status_code=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"msg= str(e), status_code={status.HTTP_400_BAD_REQUEST}, request_path={request.url}")

        return JSONResponse(content={"msg": str(e), "status": "Fail"}, status_code=status.HTTP_400_BAD_REQUEST)

@app.post('/login') 
async def login_page(request:Request,user:LoginRequest,Authorize: AuthJWT = Depends()):
    
        user_id = dbs.query(ModelBook).filter(ModelBook.email == user.email).first()   
        if user_id and verify_password(user.password,user_id.password):
            access_token = Authorize.create_access_token(subject=user.email,fresh=True)
            refresh_token = Authorize.create_refresh_token(subject=user.email)
            message_for_frontend = {
                      "msg": "login successful mr." + user_id.firstname + " " + user_id.lastname,
                      "status":"success",
                      "tokens": {"access_token": access_token, "refresh_token": refresh_token}
                    }
            logger.info(f"msg: login successful, status: success, status_code={status.HTTP_200_OK}, request_path={request.url}")

            return JSONResponse(content=message_for_frontend, status_code=status.HTTP_200_OK)
        else:
            message={
                "msg":"Entered Credentials Is Incorrect",
                "status":"error",
            }
            logger.error(f"msg={message},status_code={status.HTTP_401_UNAUTHORIZED},request_path={request.url}")
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
    
@app.put('/change_password')
def decode_access_token(request:Request,user:ChangePasswordRequest,Authorize: AuthJWT = Depends()):
    try:
        Authorize.fresh_jwt_required()
        
        decoded_token = Authorize.get_raw_jwt()
        user_email = decoded_token['sub']
        if len(user.new_password) < 8:
            logger.error(f"msg=Password is too weak it should be more than 8 characters,status_code={status.HTTP_400_BAD_REQUEST},request_path={request.url}")
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
                logger.info(f"message={message_for_frontend},status_code={status.HTTP_200_OK},request_path={request.url}")
                return JSONResponse(content=message_for_frontend,status_code=200)
             
        else :
            msg={
                "message":"Incorrect Password",
                "status":"error",
            }
            logger.error(f"message={msg},status_code={status.HTTP_400_BAD_REQUEST},request_path={request.url}")
            return JSONResponse(content="Incorrect Password",status_code=status.HTTP_400_BAD_REQUEST) 
    except IntegrityError as e:
        msg={
                "message":"Check Credentials",
                "status":"error",
            }
        logger.error(f"message={msg},request_path=%s,status_code={status.HTTP_400_BAD_REQUEST},request_path={request.url}")
        return JSONResponse(content="Check Credentials ", status_code=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"msg={str(e.message)},status_code={status.HTTP_400_BAD_REQUEST},request_path={request.url}")
        return JSONResponse(content={'status_code':status.HTTP_400_BAD_REQUEST, 'message':e.message}, status_code=status.HTTP_400_BAD_REQUEST)
    
    # except  as e:
    #     return JSONResponse(content="Invalid Token",status_code=status.HTTP_400_BAD_REQUEST )

@app.post('/refresh')
def refresh(request:Request,Authorize: AuthJWT = Depends()):
    """
    The jwt_refresh_token_required() function insures a valid refresh
    token is present in the request before running any code below that function.
    we can use the get_jwt_subject() function to get the subject of the refresh
    token, and use the create_access_token() function again to make a new access token
    """
    Authorize.jwt_refresh_token_required()
    

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user,fresh=True)
    msg={
                "message":"Authenticate Success",
                "status":"Success",
            }
    logger.info(f"message={msg},status_code={status.HTTP_200_OK},request_path={request.url}")
    return {"access_token": new_access_token,"status_code":status.HTTP_200_OK}
    
@app.put("/forgotpassword/{email_input}")
async def send_with_template(request:Request,email_input: str = Path(...)):
    random_number = random.randint(1000, 9999)

    try:
      db_books = dbs.query(ModelBook).filter(ModelBook.email == email_input).first()
      db_book = db.session.query(ModelBook).get(db_books.id)
      db_book.otp=random_number
      db.session.commit()    
      message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=[email_input],
        body="Your otp for forget password is "+str(random_number)+ "<br> this otp will expire in 5 minutes",
        subtype=MessageType.html,
        )

      fm = FastMail(conf)
      await fm.send_message(message, template_name="email_template.html") 
      msg={
                "message":":Email has been sent successfully",
                "status":"Success",
            }
      logger.info(f"message={msg},status_code={status.HTTP_200_OK},request_path={request.url}")
      return JSONResponse(status_code=200, content={"status_code":status.HTTP_200_OK,"message": "Email has been sent successfully."})
    except Exception as e:
        message_for_frontend={
            "statusCode":400,
            "message":"Entered User id is Invalid..",
            "status":"Fail"
        }
        logger.error(f"message={message_for_frontend},status_code={status.HTTP_400_BAD_REQUEST},request_path={request.url}")
        return JSONResponse(content=message_for_frontend, status_code=status.HTTP_400_BAD_REQUEST)
    
    
@app.post("/forgotchangepassword")
async def forgotpassword(details: Forgotchangepassword,request: Request):
    try:
        if details.otp != "string":
            dbbook = dbs.query(ModelBook).filter(ModelBook.otp == str(details.otp)).first()
            db_book = db.session.query(ModelBook).get(dbbook.id)
        else:
            logger.error(f"message=Invalid OTP,status_code={status.HTTP_400_BAD_REQUEST},request_path={request.url}")
            raise Exception("Invalid OTP")  # Raise an exception when OTP is "string"
    except Exception as e:
        message_for_frontend = {
            "status_code": 400,
            "message": "Invalid OTP",
        }
        logger.error(f"message={message_for_frontend},status_code={status.HTTP_400_BAD_REQUEST},request_path={request.url}")
        return JSONResponse(content=message_for_frontend, status_code=status.HTTP_400_BAD_REQUEST)

    if len(details.new_password) < 8:
        message_For_Front_end = {
            "statuscode": 400,
            "message": "password not reached the requirements is should be more than 7 characters"
        }
        logger.error(f"message={message_for_frontend},status_code={status.HTTP_400_BAD_REQUEST},request_path={request.url}")
        return JSONResponse(content=message_For_Front_end, status_code=status.HTTP_400_BAD_REQUEST)
    if details.new_password == details.confirm_password:
        newpass = get_password_hash(details.new_password)
        db_book.password = newpass
        db_book.otp = "string"
        db.session.commit()
        message = MessageSchema(
            subject="Fastapi-Mail module",
            recipients=[dbbook.email],
            body="Your Password changed successfully",
            subtype=MessageType.html,
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
        message_for_frontend = {
            "status_code": 200,
            "message": "Password changed Successfully",
            "status": "Success",
        }
        logger.error(f"message={message_for_frontend},status_code={status.HTTP_200_OK},request_path={request.url}")
        return JSONResponse(content=message_for_frontend, status_code=status.HTTP_200_OK)

    else:
        message_for_frontend = {
            "statusCode": 400,
            "message": "both password is mismatch...",
            "status": "Fail",
        }
        logger.error(f"message={message_for_frontend},status_code={status.HTTP_400_BAD_REQUEST},request_path={request.url}")
        return JSONResponse(content=message_for_frontend, status_code=status.HTTP_400_BAD_REQUEST)
