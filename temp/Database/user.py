from sqlalchemy import Column, String, Text
from .make_table import Base

#Schema 정의
class User(Base):
  __tablename__ = 'Users'
  id = Column(String(80), primary_key=True)
  password = Column(String(80), unique=True, nullable=False)  #should be hashed
  username = Column(String(120), unique=True, nullable=False)
  email = Column(Text(), unique=True, nullable=False)
  grouplist = Column(Text())  #리스트로 처리