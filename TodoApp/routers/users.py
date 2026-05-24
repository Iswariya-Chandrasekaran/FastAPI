from http.client import HTTPException
from fastapi import APIRouter,Depends,status,HTTPException,Path
from typing import Annotated
from ..models import Users
from ..database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_cur_user
from passlib.context import CryptContext
from pydantic import BaseModel
router=APIRouter(prefix="/users",tags=["users"])

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Annotated[DATATYPE, DEPENDENCY]
db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_cur_user)]
bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated=['auto'])

class UserVerification(BaseModel):
    old_password: str
    new_password: str

@router.get("/",status_code=status.HTTP_200_OK)
async def get_user(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    return db.query(Users).filter(Users.id==user.get('id')).first()

# @router.put("/{user_id}",status_code=status.HTTP_200_OK)
# async def change_password(user:user_dependency,db:db_dependency,
#                           new_password:str,user_id:int=Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
#     update_user=db.query(Users).filter(Users.id==user_id).first()
#     if update_user is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
#     update_user.hashed_password=bcrypt_context.hash(new_password)
#     db.add(update_user)
#     db.commit()

#prob: we will give old password then give new password.
# otherwise anyone can change it
@router.put("/change",status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user:user_dependency,db:db_dependency,
                          user_verify:UserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    update_user=db.query(Users).filter(Users.id==user.get('id')).first()
    if update_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if not bcrypt_context.verify(user_verify.old_password,update_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Incorrect password")
    update_user.hashed_password=bcrypt_context.hash(user_verify.new_password)
    db.add(update_user)
    db.commit()

@router.put("/profile-update", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user:user_dependency,db:db_dependency,
                           phone_number:str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    update_user=db.query(Users).filter(Users.id==user.get('id')).first()
    if update_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    update_user.phone_number=phone_number
    db.add(update_user)
    db.commit()