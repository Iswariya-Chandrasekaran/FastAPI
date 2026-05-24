from ..routers.auth import get_cur_user
from ..routers.todos import get_db
from fastapi import status
from .utils import *

app.dependency_overrides[get_db]=override_get_db
app.dependency_overrides[get_cur_user]=override_get_cur_user


def test_read_user_todos(get_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "id":1,
        "title": "Pytest",
        "description" : "Learn testing",
        "completed" : False,
        "priority" : 1,
        "owner_id": 1}]

def test_read_todo_authenticated(get_todo):
    response = client.get("/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id":1,
        "title": "Pytest",
        "description" : "Learn testing",
        "completed" : False,
        "priority" : 1,
        "owner_id": 1}

def test_read_todo_not_authenticated():
    response = client.get("/todos/todo/87")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" :"Todo with id 87 is not found"}


def test_create_todo(get_todo):
    request_data = {
        "title": "Sleep",
        "description" : "Learn to sleep early",
        "completed" : False,
        "priority" : 3,
    }
    response = client.post("/todos/create-todo", json = request_data)
    assert response.status_code == 201
    db = TestSessionLocal()
    new_todo = db.query(Todos).filter(Todos.id==2).first()
    assert new_todo.title == request_data.get('title')
    assert new_todo.description == request_data.get('description')
    assert new_todo.completed == request_data.get('completed')
    assert new_todo.priority == request_data.get('priority')

def test_update_todo(get_todo):
    request_data = {
        "title": "Pytest",
        "description" : "Learn testing",
        "priority" : 2,
        "completed" : False,
    }
    response = client.put("/todos/todo/1", json = request_data)
    assert response.status_code == 204
    db=TestSessionLocal()
    model=db.query(Todos).filter(Todos.id== 1).first()
    assert model.title == request_data.get('title')
    assert model.priority == request_data.get('priority')

def test_update_todo_not_found(get_todo):
    request_data = {
        "title": "Pytest",
        "description" : "Learn testing",
        "priority" : 2,
        "completed" : False,
    }
    response = client.put("/todos/todo/6", json = request_data)
    assert response.status_code == 404
    assert response.json() == {"detail":"Todo not Found"}

def test_delete_todo(get_todo):
    response = client.delete("/todos/todo/1")
    assert response.status_code == 204
    db=TestSessionLocal()
    model=db.query(Todos).filter(Todos.id== 1).first()
    assert model is None

def test_delete_todo_not_found(get_todo):
    response = client.delete("/todos/todo/100")
    assert response.status_code == 404
    assert response.json()=={"detail":"Todo with id 100 is not found"}
