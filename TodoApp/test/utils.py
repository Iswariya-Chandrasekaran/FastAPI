from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from ..database import Base
from ..main import app
from fastapi.testclient import TestClient
import pytest
from ..models import Todos, Users
from passlib.context import CryptContext

SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       connect_args={"check_same_thread": False},
                       poolclass=StaticPool)

TestSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base.metadata.create_all(engine)

def override_get_db():
    db=TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_cur_user():
    return {"username":"tester", "email":"tester@gmail", "role":"admin", "id":1}

client = TestClient(app)

@pytest.fixture
def get_todo():
    test_todo = Todos(
        title= "Pytest",
        description = "Learn testing",
        completed = False,
        priority = 1,
        owner_id = 1
    )

    db=TestSessionLocal()
    db.add(test_todo)
    db.commit()
    yield test_todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated=['auto'])

@pytest.fixture
def test_user():
    test_user = Users(
        email="tester@gmail",
        username="tester",
        first_name="tester",
        last_name="1",
        is_active=True,
        role="admin",
        hashed_password=bcrypt_context.hash("test@123"),
        phone_number="1234567890"
    )
    db=TestSessionLocal()
    db.add(test_user)
    db.commit()
    yield test_user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()