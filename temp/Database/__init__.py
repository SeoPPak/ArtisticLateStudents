from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .import user
from .make_table import Base

#SQLite 연동?
engine = create_engine('sqlite:///example.db', echo=True)

#ORM 저장할 Session 정의
Session = sessionmaker(bind=engine)
session = Session()