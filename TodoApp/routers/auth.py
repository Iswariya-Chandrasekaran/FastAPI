from http.client import HTTPException
from fastapi import APIRouter,Depends,status,HTTPException,Request
from typing import Annotated,Any
from pydantic import BaseModel
from ..models import Users
from ..database import SessionLocal
from sqlalchemy.orm import Session
# Password hashing manager from passlib.Used for password hashing + verification
from passlib.context import CryptContext
# Automatically gets username/password from login form,
# OAuth2PasswordBearer-looks for the token in the Authorization header & handle it validation.
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
# Used for JWT token creation and verification.
from jose import jwt,JWTError
# Used for token expiry time calculations.
from datetime import timedelta, datetime, timezone
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

router=APIRouter(prefix="/auth",tags=["auth"])
# Secret key used to create sign.Should be kept private.
SECRET_KEY='dc04cf166f36a81f90ff45928227d64479de6805707f3112924913fff8a322de'
# Signing algorithm for JWT Header.
ALGORITHM='HS256'

# Request body model for signup
# Defines what fields are expected from frontend.
class CreateRequestUser(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str
# Response model for login API
# Defines structure of returned JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]
# Creating password hashing configuration.
# schemes=["bcrypt"] tells passlib: "Use bcrypt algorithm"
# bcrypt is secure password hashing algorithm.
# deprecated="auto" handles old algorithm management automatically.
bcrypt_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme configuration
# Token url tells swagger UI where login API exists
oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

templates = Jinja2Templates(directory="TodoApp/templates")

####Pages####
@router.get("/login-page") # Route for the home page
def render_login_page(request:Request):
    # Render home.html template and pass the request object to Jinja2
    return templates.TemplateResponse(request=request,
                                      name="login.html",
                                      context={"request":request}
                                      )

@router.get("/register-page") # Route for the home page
def render_register_page(request:Request):
    # Render home.html template and pass the request object to Jinja2
    return templates.TemplateResponse(request=request,
                                      name="register.html",
                                      context={"request":request}
                                      )
### Endpoints###
# Function used to verify user credentials.Checks:
# 1. Username exists?
# 2. Password matches hashed password?
def authenticate_user(username:str, password: str,db):
    cur_user=db.query(Users).filter(Users.username==username).first()
    if not cur_user:
        return False
    if not bcrypt_context.verify(password,cur_user.hashed_password):
        return False
    return cur_user

# Function used to create JWT access token. Adds:
# 1. Username 2. User ID 3. Expiry time
# Then signs token using secret key and algo
def create_access_token(username: str, user_id :int,role:str, expiry: timedelta):
    payload:dict[str,Any] = {'sub': username, 'id': user_id, 'role':role}
    expires = datetime.now(timezone.utc)+expiry
    payload['exp']=expires
    return jwt.encode(payload, SECRET_KEY,algorithm=ALGORITHM)

# Function used to get current logged-in user from JWT token.
# This runs automatically for protected routes. used as dependency injection in other file
async def get_cur_user(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        # Decoding and verifying JWT token.
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id:int = payload.get('id')
        user_role: str = payload.get('role')
        # If required data missing in token.
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not validate credentials')
        return {'username': username, 'id': user_id, 'role':user_role}
    except JWTError: # Handles:invalid, expired,tampered token
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED
        , detail = 'Could not validate credentials')

# User registration API-Creates new user account in DB.
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,user_request: CreateRequestUser):
    # Creates a sqlalchemy object so could access test_user.id
    # not like test_user.get('id') or test_user["id"]
    user_detail=Users(
        username=user_request.username,
        email=user_request.email,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        role=user_request.role,
        hashed_password=bcrypt_context.hash(user_request.password),
        is_active=True,
        phone_number=user_request.phone_number
    )
    db.add(user_detail)
    db.commit()

# Login API - Verifies username/password and returns JWT token.
# Server creates JWT token
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):
    user=authenticate_user(form_data.username,form_data.password,db)
    if not user:
        return "Failed Authentication"
    # Creating JWT token with 10 minute expiry.
    token=create_access_token(user.username,user.id,user.role, timedelta(minutes=10))
    # Returning JWT token response.
    return {"access_token":token,"token_type":"bearer" }
