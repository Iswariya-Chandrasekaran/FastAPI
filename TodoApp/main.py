# FastAPI framework and dependency injection tool
from fastapi import FastAPI,Request,status
from  .models import Base
from .database import engine
from .routers import auth,todos,admin,users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
app=FastAPI()

# Create all database tables defined in models (runs at startup)
Base.metadata.create_all(bind=engine)

# Mount static files folder (CSS, JS, Images) to serve static content
app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")
@app.get("/") # Route for the home page
def test(request:Request):
    # Render home.html template and pass the request object to Jinja2
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

@app.get("/health")
def healthy_check():
    return {"status": "Healthy"}
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)

app.include_router(users.router)