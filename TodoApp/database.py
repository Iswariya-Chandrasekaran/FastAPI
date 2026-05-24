#
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
#
# #used to create a location for this db in our fastapi application
# SQLALCHEMY_DATABASE_URL='sqlite:///./todosapp.db'
#
# #engine used to connect db to python application
# # can access sqlite with only 1 thread but fastapi uses multiple thread so we are disabling
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# #session maker is the factory , using local we get session then we will use it
# #fastapi>>session local>>engine>>database
# SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
#
# # base is parent class which tells it's child class are tables
# Base=declarative_base()

# ----------------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#used to create a location for this db in our fastapi application
SQLALCHEMY_DATABASE_URL='postgresql://postgres:cmai%401609@localhost/TodosApplicationDatabase'

#engine used to connect db to python application
# can access sqlite with only 1 thread but fastapi uses multiple thread so we are disabling
engine = create_engine(SQLALCHEMY_DATABASE_URL)
#session maker is the factory , using local we get session then we will use it
#fastapi>>session local>>engine>>database
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

# base is parent class which tells it's child class are tables
Base=declarative_base()