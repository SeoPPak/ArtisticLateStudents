from app.database import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import hashlib

class Group(db.Model):
  __tablename__ = "Group"
  id = db.Column(db.Integer(), primary_key=True, nullable=False)
  name = db.Column(db.Text(), nullable=False)
  schedules = relationship('Schedule', backref='group', cascade="all")
  notices = relationship('Notice', backref='group', cascade="all")
  register_infos = relationship('Register_Info', backref='group', cascade="all")
  invite_codes = relationship('InviteCode', backref='group', cascade="all")
  moneylists = relationship('MoneyList', backref='group', cascade="all")

  def __init__(self, id, name):
    self.id = id
    self.name = name

class User(db.Model):
  __tablename__ = "User"
  id = db.Column(db.Integer(), primary_key=True)
  password = db.Column(db.Text(), nullable=False)  #should be hashed
  username = db.Column(db.String(120), nullable=False)
  email = db.Column(db.Text(), unique=True, nullable=False)
  register_infos = relationship('Register_Info', backref='user', cascade="all")

  def __init__(self, id, password, username, email):
    self.id = id
    self.password = str(hashlib.sha512(password.encode()).hexdigest())
    self.username = username
    self.email = email

  def checkID(self, id, pw):
    if self.id == id and self.password == str(hashlib.sha512(pw.encode()).hexdigest()):
      return True
    else:
      return False

  def __eq__(self, other):
    return self.checkID(other.id, other.password)

  def __ne__(self, other):
    return not self.checkID(other.id, other.password)


class Register_Info(db.Model):
  __tablename__ = "Register_Info"
  __table_args__ = (db.PrimaryKeyConstraint('user_id', 'group_id', name='register_info_uc'), )

  user_id = db.Column(db.Integer(), ForeignKey('User.id'), nullable=False)
  group_id = db.Column(db.Integer(), ForeignKey('Group.id'), nullable=False)
  admin = db.Column(db.Boolean(), nullable=False)

  def __init__(self, u_id, g_id, admin):
    self.user_id = u_id
    self.group_id = g_id
    self.admin = admin

class Schedule(db.Model):
  __tablename__ = "Schedule"

  schedule_id = db.Column(db.Integer(), primary_key=True)
  group_id = db.Column(db.Integer(), ForeignKey('Group.id'), nullable=False)
  name = db.Column(db.Text(), nullable=False)
  date = db.Column(db.Date(), nullable=True)

  def __init__(self, s_id, g_id, name, date):
    self.schedule_id = s_id
    self.group_id = g_id
    self.name = name
    self.date = date

class Notice(db.Model):
  __tablename__ = "Notice"

  notice_id = db.Column(db.Integer(), primary_key=True)
  group_id = db.Column(db.Integer(), ForeignKey('Group.id'), nullable=False)
  name = db.Column(db.Text(), nullable=False)
  content = db.Column(db.Text(), nullable=False)

  def __init__(self, n_id, g_id, name, content):
    self.notice_id = n_id
    self.group_id = g_id
    self.name = name
    self.content = content

class InviteCode(db.Model):
  __tablename__ = "InviteCode"
  code = db.Column(db.Text(), primary_key=True, nullable=False)
  group_id = db.Column(db.Integer(), ForeignKey('Group.id'),nullable=False)
  limit_date = db.Column(db.Date(), nullable=False)

  def __init__(self, code, g_id, limit):
    self.group_id = g_id
    self.limit_date = limit
    self.code = code


class MoneyList(db.Model):
  __tablename__ = "MoneyList"

  moneydata_id = db.Column(db.Integer(), primary_key=True)
  group_id = db.Column(db.Integer(), ForeignKey('Group.id'), nullable=False)
  name = db.Column(db.Text(), nullable=False)
  date = db.Column(db.Date(), nullable=False)
  value = db.Column(db.Integer(), nullable=False)
  sval = db.Column(db.Integer(), nullable=False)

  def __init__(self, moneydata_id, group_id, name, date, value, sval):
    self.moneydata_id = moneydata_id
    self.group_id = group_id
    self.name = name
    self.date = date
    self.value = value
    self.sval = sval