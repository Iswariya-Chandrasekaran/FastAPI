import pytest

def test_bool():
    validated=True
    assert validated is True
    assert ("hello"=="world") is False

def test_type():
    assert type(3 is int)
    assert type('3' is not int)
    assert type('5ch' is str)

def test_instances():
    assert isinstance('testing', str)
    assert not isinstance('3', int)

def test_list():
    num_list=[1, 2, 3, 6, 3]
    any_list=[False, False]
    assert 3 in num_list
    assert 10 not in num_list
    assert all(num_list)
    assert not any(any_list)

class Student:
    def __init__(self,name:str,age: int, grade: int):
        self.name = name
        self.age = age
        self.grade = grade

def test_object():
    student1 = Student("Arul", 14, 9)
    assert student1.name == "Arul"
    assert student1.age == 14
    assert not student1.grade == 10

class Employee:
    def __init__(self,name:str,age: int, department: str):
        self.name = name
        self.age = age
        self.department = department

@pytest.fixture
def default_employee():
    return Employee("Rathna", 41, "Sales")

def test_employee(default_employee):
    assert default_employee.name == "Rathna"
    assert default_employee.age == 41
    assert not default_employee.department == "HR"
