from typing import Annotated  # Used to combine type (Session) with dependency (Depends)
from fastapi import APIRouter, Depends,HTTPException, status, Path, Request  # FastAPI framework and dependency injection tool
from passlib.handlers.django import django_pbkdf2_sha1
from sqlalchemy.orm import Session  # Session is used to interact with the database
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from ..models import Todos
from ..database import SessionLocal
from pydantic import BaseModel, Field
from .auth import get_cur_user

router=APIRouter(
    prefix = "/todos",
    tags=['todos']
)

class RequestTodo(BaseModel):
    title: str =Field(min_length=1)
    description: str =Field(min_length=1, max_length=100)
    priority: int = Field(gt=0)
    completed: bool = False

#Dependency function to get DB session
def get_db():
    db=SessionLocal() # Creates new db session (connection)
    try:
        yield db # Gives the session to API request
    finally:
        db.close() # closes session when request completed

db_dependency=Annotated[Session, Depends(get_db)]

user_dependency=Annotated[dict,Depends(get_cur_user)]

templates = Jinja2Templates(directory="TodoApp/templates")

def redirect_to_login():
    redirect_response=RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response
### Pages ###
@router.get("/todo-page")
async def render_todo_page(request: Request, db:db_dependency):
    try:
        user = await get_cur_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todos=db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
        return templates.TemplateResponse(request=request,
                                          name="todos.html",
                                          context={"request":request, "todos":todos, "user":user})
    except Exception as e:
        print(e)
        return redirect_to_login()

@router.get("/add-todo-page")
async def render_todo_page(request:Request):
    try:
        user=await get_cur_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse(request=request,
                                          name="add-todo.html",
                                          context={"request":request,"user":user})
    except:
        return redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request:Request, todo_id:int, db:db_dependency):
    try:
        user=await get_cur_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todo=db.query(Todos).filter(Todos.id == todo_id).first()
        return templates.TemplateResponse(request=request,
                                          name="edit-todo.html",
                                          context={"request":request, "todo":todo, "user":user})
    except:
        return redirect_to_login()
### Endpoints ###
@router.get("/")
async def read_user_todos(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")
    # db.query(Todos)- select all records from Todos table
    # execute query and return all records as list
    return db.query(Todos).filter(Todos.owner_id==user.get('id')).all()
@router.get("/todo/{todos_id}", status_code=status.HTTP_200_OK)
async def search_todos(user:user_dependency,db:db_dependency,todos_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")
    todo_model=db.query(Todos).filter(Todos.id==todos_id)\
        .filter(Todos.owner_id==user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail=f"Todo with id {todos_id} is not found")
    return todo_model

@router.post("/create-todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db:db_dependency, todo_content:RequestTodo):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")
    # update owner id with id in user (after converting header to user data)
    todo_model=Todos(**todo_content.model_dump(),owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()

@router.put("/todo/{todos_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user:user_dependency, db:db_dependency,todo_update_content:RequestTodo,todos_id: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")
    todo_model=db.query(Todos).filter(Todos.id==todos_id)\
        .filter(Todos.owner_id==user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not Found")
    todo_model.title=todo_update_content.title
    todo_model.description=todo_update_content.description
    todo_model.priority=todo_update_content.priority
    todo_model.completed=todo_update_content.completed

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todos_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db:db_dependency, todos_id: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")
    todo_model=db.query(Todos).filter(Todos.id==todos_id)\
        .filter(Todos.owner_id==user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todos_id} is not found")
    db.query(Todos).filter(Todos.id==todos_id)\
        .filter(Todos.owner_id==user.get('id')).delete()
    db.commit()
