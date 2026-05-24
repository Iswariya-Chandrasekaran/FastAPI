from ..routers.admin import get_cur_user, get_db
from .utils import *
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_cur_user] = override_get_cur_user

def test_all_todo_authenticated(get_todo):
    response = client.get("/admin/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"id":1,
        "title": "Pytest",
        "description" : "Learn testing",
        "completed" : False,
        "priority" : 1,
        "owner_id": 1}]

def test_delete_todo_authenticated(get_todo):
    response = client.delete("/admin/todos/1")
    assert response.status_code == 204
    db=TestSessionLocal()
    todo=db.query(Todos).filter(Todos.id==1).first()
    assert todo is None

def test_delete_not_found_todo_authenticated(get_todo):
    response = client.delete("/admin/todos/99")
    assert response.status_code == 404
    assert response.json() == {"detail":"Todo with 99 id not found"}