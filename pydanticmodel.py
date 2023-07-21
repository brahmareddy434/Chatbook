from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class ChangePasswordRequest(BaseModel):
    password: str
    new_password: str
    confirm_password:str
class Forgotchangepassword(BaseModel):
    otp : int
    new_password : str
    confirm_password : str



class Register(BaseModel):
    firstname :str
    lastname :str
    email :str
    password :str
    mobile_number:str
    age :int
    