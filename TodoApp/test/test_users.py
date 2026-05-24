from .utils import *
from ..routers.users import get_db, get_cur_user
from fastapi import status

app.dependency_overrides[get_db]= override_get_db
app.dependency_overrides[get_cur_user]=override_get_cur_user

def test_get_user(test_user):
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json()["username"]== "tester"
    assert response.json()["email"]== "tester@gmail"
    assert response.json()["first_name"]== "tester"
    assert response.json()["last_name"]== "1"
    assert response.json()["phone_number"]== "1234567890"
    assert response.json()["role"]== "admin"


def test_password_change(test_user):
    response = client.put("/users/change", json={"old_password":"test@123", "new_password":"testing"})
    assert response.status_code == 204

#Not giving user so it couldn't find user
def test_password_not_authenticated():
    response = client.put("/users/change", json={"old_password":"test@123", "new_password":"testing"})
    assert response.status_code == 404
    assert response.json() == {"detail":"User not found"}

# Giving wrong old password.
def test_password_change_invalid_password(test_user):
    response = client.put("/users/change", json={"old_password":"wrong@password", "new_password":"testing"})
    assert response.status_code == 403
    assert response.json() =={"detail":"Incorrect password"}

# example on how to pass query param in url
def test_phone_number_update(test_user):
    response = client.put("/users/profile-update?phone_number=9876543210")
    assert response.status_code == 204
    db=TestSessionLocal()
    updated_user = db.query(Users).filter(Users.id==test_user.id).first()
    assert updated_user.phone_number == "9876543210"
