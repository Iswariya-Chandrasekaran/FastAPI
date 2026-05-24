from http.client import HTTPException
from fastapi import APIRouter,Depends,status,HTTPException,Path
from typing import Annotated
from ..models import Todos
from ..database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_cur_user

router=APIRouter(prefix="/admin",tags=["admin"])

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Annotated[DATATYPE, DEPENDENCY]
db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_cur_user)]

@router.get("/todos",status_code=status.HTTP_200_OK)
async def get_all_admin_todos(user:user_dependency,db:db_dependency):
    if user is None or user.get('role') !="admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Admin privilege")
    return db.query(Todos).all()

@router.delete("/todos/{todos_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,db:db_dependency,todos_id:int=Path(gt=0)):
    if user is None or user.get('role') != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Admin privilege"                        )
    todo=db.query(Todos).filter(Todos.id==todos_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Todo with {todos_id} id not found")
    db.query(Todos).filter(Todos.id==todos_id).delete()
    db.commit()


