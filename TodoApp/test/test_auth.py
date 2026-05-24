from .utils import *
from ..routers.auth import (get_db,get_cur_user,authenticate_user
, create_access_token,SECRET_KEY, ALGORITHM)
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_cur_user]=override_get_cur_user

def test_is_user_authenticated(test_user):
    db=TestSessionLocal()
    user = authenticate_user("tester","test@123",db)
    assert user is not None
    assert user.username == "tester"
    # we can do the same for wrong password user
    invalid_user = authenticate_user("invalid@user","test@123",db)
    assert invalid_user is False

    wrong_password = authenticate_user("tester","wrong-password",db)
    assert wrong_password is False

# test if the create access token creates the token once if
# it created we are checking by decoding the created token
def test_create_access_token():
    username ="tester"
    user_id =1
    role ="admin"
    expiry = timedelta(days=1)
    access_token=create_access_token(username, user_id, role, expiry)

    decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms= [ALGORITHM],
                               options={'verify_signature': False})
    assert decoded_token['sub'] == username
    assert decoded_token['role'] == role
    assert decoded_token['id'] == user_id

@pytest.mark.asyncio
async def test_validate_get_cur_user():
    # this function needs token so create one
    encode = {'sub':"tester", "id":1, "role":"admin"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    #the below fn will return this dict {'username': username, 'id': user_id,
    # 'role':user_role}
    cur_user =await get_cur_user(token)
    assert cur_user['username'] == "tester"
    assert cur_user == {'username': 'tester', 'id': 1, 'role': 'admin'}

# test if get_cur_user creates raises error if a detail missing in payload
@pytest.mark.asyncio
async def test_validate_get_user_missing_payload():
    encode = {'sub': "tester"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
  # expect get_cur_user(token) to raise HTTPException.
  # Without pytest.raises(): exception would crash test.
    with pytest.raises(HTTPException) as e:
        await get_cur_user(token)

    assert e.value.status_code == 401
    assert e.value.detail == "Could not validate credentials"