from app import db, request
from sqlalchemy import and_, select
import json
from app import User, Group, Schedule, Notice, Register_Info, InviteCode, MoneyList
import app
import pandas as pd
import hashlib
import random
from random import randrange as rand
import uuid
import base64
import codecs
from datetime import datetime, timedelta
import requests
import time
import os

app = app.create_app()


@app.route('/', methods=['POST', 'GET'])
def start():
  return '{"임시"}', 200


@app.route('/login', methods=['POST', 'GET'])
def login():
  email = request.args.get("email")
  pw = request.args.get("pw")

  if email is None or pw is None:
    result = {"logged in": "false", "error": "wrong parameter"}
    return json.dumps(result)

  pw = str(hashlib.sha512(pw.encode()).hexdigest())

  user = User.query.filter_by(email=str(email)).filter_by(
    password=str(pw)).limit(1).one_or_none()

  print(user)

  if user is not None:
    return json.dumps({"logged in": "true"})
  else:
    return json.dumps({"logged in": "false"})


@app.route('/checkID', methods=['POST', 'GET'])
def checkID():
  id = request.args.get("id")
  if id is None:
    result = {"duplicated": "false", "error": "wrong parameter"}
    return json.dumps(result)
  user = User.query.filter_by(id=id).limit(1).one_or_none()

  if user is None:
    return json.dumps({"duplicated": "true"})
  else:
    return json.dumps({"duplicated": "false"})


@app.route('/signup', methods=['POST', 'GET'])
def signup():
  id = rand(1000000000)
  id = str(id)
  valid = User.query.filter_by(id=id).limit(1).one_or_none()
  while valid is not None:
    id = rand(1000000000)
    valid = User.query.filter_by(id=id).limit(1).one_or_none()

  pw = request.args.get("pw")
  username = request.args.get("username")
  email = request.args.get("email")
  if email is None or pw is None or username is None:
    result = {"registered": "false", "error": "wrong parameter"}
    return json.dumps(result)

  user = User(id=id, password=pw, username=username, email=email)

  try:
    db.session.add(user)
    db.session.commit()
    return json.dumps({"registered": "true"})
  except:
    return json.dumps({"registered": "false"})


@app.route('/user/list', methods=['POST', 'GET'])
def userList():
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  user_set = User.query.filter(User.username.is_not(None))
  df = pd.read_sql(str(user_set.statement), user_set.session.bind)
  print(df)
  return json.loads(df.to_json(force_ascii=False, orient='records'))


@app.route('/user/<userID>', methods=['POST', 'GET'])
def userInform(userID):
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  user = User.query.filter(User.email == str(userID))
  if user is not None:
    df = pd.read_sql(user.statement, user.session.bind)
    return json.loads(df.to_json(force_ascii=False, orient='records'))
  else:
    return json.dumps({"user exist": "false"})


@app.route('/user/join/<userID>/<inviteCode>')
def join(userID, inviteCode):
  user = User.query.filter(User.id == str(userID)).one_or_none()
  if user is None:
    return json.dumps({"error": "user not exist"})

  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  ic = InviteCode.query.filter_by(code=str(inviteCode)).one_or_none()
  print("after df")
  if ic is None:
    result = {"joined": "false"}
    return json.dumps(result)

  valid = ic.limit_date >= datetime.date(datetime.today())
  if valid is False:
    result = {"joined": "false"}
    return json.dumps(result)

  groupID = ic.group_id
  group = Group.query.filter_by(id=int(groupID)).one()
  print("before add")
  register_info = Register_Info(u_id=userID, g_id=groupID, admin="false")
  try:
    db.session.add(register_info)
    db.session.commit()
    result = {"joined": "true", "group": {"id": group.id, "name": group.name}}

    return json.dumps(result, ensure_ascii=False)
  except:
    return {"joined": "false"}


@app.route('/user/group')
def joinedGroup():
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  userID = request.args.get("user_id")
  if userID is None:
    result = {"joined": "false", "error": "wrong parameter"}
    return json.dumps(result)
  user = User.query.filter(User.id == userID).one_or_none()
  if user is None:
    result = {"error": "no user exists"}
    return json.dumps(result)

  list = select(Register_Info).join(User.register_infos)
  list = list.filter(Register_Info.user_id == int(userID))
  df = pd.read_sql(list, db.session.bind)
  if len(df) != 0:
    return json.loads(df.to_json(force_ascii=False, orient='records'))
  else:
    return json.dumps({"error": "no group exist"})


@app.route('/user/quit/<userID>', methods=['GET', 'DELETE'])
def quit(userID):
  user = User.query.filter(User.id == userID).one_or_none()
  if user is not None:
    try:
      db.session.delete(user)
      db.session.commit()
      return json.dumps({"quited": "true"})
    except:
      return json.dumps({"quited": "false"})
  else:
    return json.dumps({"quited": "false", "error": "no user exist"})


@app.route('/group/create', methods=['POST', 'GET'])
def create():
  group_id = rand(1000000000)
  group_id = str(group_id)

  valid = Group.query.filter_by(id=group_id).limit(1).one_or_none()
  while valid is not None:
    group_id = rand(1000000000)
    valid = Group.query.filter_by(id=group_id).limit(1).one_or_none()

  group_name = request.args.get("group_name")
  admin_id = request.args.get("admin_id")
  if group_name is None or admin_id is None:
    result = {"created": "false", "error": "wrong parameter"}
    return json.dumps(result)

  duplicated = Group.query.filter_by(name=group_name).limit(1).one_or_none()
  while duplicated is not None:
    result = {"created": "false", "error": "name duplicated"}
    return json.dumps(result)

  user = User.query.filter(User.id == admin_id).one_or_none()
  if user is None:
    result = {"created": "false", "error": "no user exist"}
    return json.dumps(result)

  group = Group(id=group_id, name=group_name)
  register_info = Register_Info(u_id=admin_id, g_id=group_id, admin="true")

  try:
    db.session.add(group)
    db.session.commit()

    db.session.add(register_info)
    db.session.commit()

    return json.dumps({"created": "true"})
  except:
    return json.dumps({"created": "false"})


@app.route('/group/list', methods=['POST', 'GET'])
def groupList():
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  group_set = Group.query.filter(Group.id.is_not(None))
  df = pd.read_sql(str(group_set.statement), group_set.session.bind)

  return json.loads(df.to_json(force_ascii=False, orient='records'))


@app.route('/group/<groupID>', methods=['POST', 'GET'])
def groupInform(groupID):
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  list = select(Register_Info).join(Group.register_infos)
  list = list.filter(Group.id == int(groupID))

  df = pd.read_sql(list, db.session.bind)
  if len(df) != 0:
    return json.loads(df.to_json(force_ascii=False, orient='records'))
  else:
    return json.dumps({"error": "Group not exists"})


@app.route('/group/<groupID>/inviteCode/generate',
           methods=['POST', 'GET', 'DELETE'])
def generateIC(groupID):
  ic = InviteCode.query.filter_by(group_id=groupID).limit(1).one_or_none()
  today = datetime.today()
  if ic is not None:
    if datetime.date(today) < ic.limit_date:
      return json.dumps({"generated": "false", "error": "code already exist"})
    else:
      try:
        db.session.delete(ic)
        db.session.commit()
      except:
        result = {"generated": "false"}
        return json.dumps(result)

  code = base64.urlsafe_b64encode(
    codecs.encode(uuid.uuid4().bytes, "base64").rstrip()).decode()[:8]
  limitDate = today + timedelta(days=7)
  invitecode = InviteCode(code=code, g_id=groupID, limit=limitDate)

  try:
    db.session.add(invitecode)
    db.session.commit()
    return json.dumps({"generated": "true", "code": code})
  except:
    return json.dumps({"generated": "false"})


@app.route('/group/inviteCode/<groupID>')
def showIC(groupID):
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  ic = select(InviteCode).join(Group.invite_codes)
  ic = ic.filter(Group.id == int(groupID))
  df = pd.read_sql(ic, db.session.bind)
  if len(df) != 0:
    return json.loads(df.to_json(force_ascii=False, orient='records'))
  else:
    generateIC(groupID)
    return showIC(groupID)


@app.route('/check/inviteCode')
def checkIC():
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  code = request.args.get("code")
  if code is None:
    result = {"created": "false", "error": "wrong parameter"}
    return json.dumps(result)

  invitecode = InviteCode.query.filter(InviteCode.code == str(code))
  df = pd.read_sql(invitecode.statement, invitecode.session.bind)

  if len(df) == 0:
    result = {"valid": "false"}
    return json.dumps(result)

  valid = df["limit_date"] >= datetime.date(datetime.today())
  if valid is False:
    result = {"valid": "false"}
    return json.dumps(result)

  groupID = df["group_id"]
  group = Group.query.filter_by(id=int(groupID)).one()
  print(group)
  result = {"group_id": group.id, "name": group.name}
  return json.dumps(result, ensure_ascii=False)


@app.route('/group/quit/<groupID>', methods=['POST', 'GET'])
def deleteGroup(groupID):
  group = Group.query.filter_by(id=groupID).one_or_none()
  if group is None:
    result = {"quited": "false", "error": "No group exist"}
    return json.dumps(result)

  try:
    db.session.delete(group)
    db.session.commit()
    return {"quited": "true"}
  except:
    result = {"quited": "false", "error": "Fail to Delete"}
    return result


@app.route('/schedule/add', methods=['POST', 'GET'])
def addSchedule():
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  id = rand(1000000000)
  id = str(id)
  valid = Schedule.query.filter_by(schedule_id=id).limit(1).one_or_none()
  while valid is not None:
    id = rand(1000000000)
    valid = Schedule.query.filter_by(id=id).limit(1).one_or_none()

  groupID = request.args.get("group_id")
  name = request.args.get("name")
  date = request.args.get("date")

  if groupID is None or name is None or date is None:
    result = {"created": "false", "error": "wrong parameter"}
    return json.dumps(result)

  group = Group.query.filter_by(id=groupID).one_or_none()
  if group is None:
    result = {"registered": "false", "error": "no group exists"}
    return json.dumps(result)

  dateformat = "%Y-%m-%d"
  date = datetime.strptime(date, dateformat)

  schedule = Schedule(id, groupID, name, date)
  try:
    db.session.add(schedule)
    db.session.commit()
    result = {
      "registered": "true",
      "schedule": {
        "schedule_id": schedule.schedule_id,
        "group_id": schedule.group_id,
        "name": schedule.name,
        "date": str(schedule.date)
      }
    }
    return json.dumps(result, ensure_ascii=False)
  except:
    result = {"registered": "false", "error": "Fail to Add"}
    return json.dumps(result)


@app.route('/schedule/user/<userID>/<fromDate>/<toDate>',
           methods=['POST', 'GET'])
def userSchedule(userID, fromDate, toDate):
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  user = User.query.filter_by(id=userID).one_or_none()
  if user is None:
    result = {"error": "user not exists"}
    return json.dumps(result)

  groupList = select(Register_Info).join(User.register_infos)
  groupList = groupList.filter(Register_Info.user_id == int(userID))
  df = pd.read_sql(groupList, db.session.bind)
  if len(df) == 0:
    result = {"error": "schedule not exists"}
    return json.dumps(result)

  groupSet = df["group_id"]
  print(groupSet)

  format = "%Y-%m-%d"
  fromDate = datetime.strptime(fromDate, format)
  fromDate = datetime.date(fromDate)

  toDate = datetime.strptime(toDate, format)
  toDate = datetime.date(toDate)
  scheduleList = []
  for groupID in groupSet:
    groupSchedule = []
    schedule = select(Schedule).join(Group.schedules)
    schedule = schedule.filter_by(group_id=int(groupID))
    df = pd.read_sql(schedule, db.session.bind)
    for i in range(len(df)):
      if fromDate < df.date[i] and toDate > df.date[i]:
        inform = {
          "schedule_id": str(df.schedule_id[i]),
          "group_id": str(df.group_id[i]),
          "name": df.name[i],
          "date": str(df.date[i])
        }
        groupSchedule.append(inform)
    if len(groupSchedule) != 0:
      scheduleList.append(groupSchedule)
  print(scheduleList)

  if len(scheduleList) != 0:
    result = {"item": scheduleList}
    return json.dumps(result, ensure_ascii=False)
  else:
    result = {"item": "no schedule exists"}
    return json.dumps(result)


@app.route('/schedule/group/<groupID>/<fromDate>/<toDate>',
           methods=['POST', 'GET'])
def groupSchedule(groupID, fromDate, toDate):
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  format = "%Y-%m-%d"
  fromDate = datetime.strptime(fromDate, format)
  fromDate = datetime.date(fromDate)

  toDate = datetime.strptime(toDate, format)
  toDate = datetime.date(toDate)

  groupSchedule = []
  schedule = select(Schedule).join(Group.schedules)
  schedule = schedule.filter_by(group_id=int(groupID))
  df = pd.read_sql(schedule, db.session.bind)
  for i in range(len(df)):
    if fromDate < df.date[i] and toDate > df.date[i]:
      inform = {
        "schedule_id": str(df.schedule_id[i]),
        "group_id": str(df.group_id[i]),
        "name": df.name[i],
        "date": str(df.date[i])
      }
      groupSchedule.append(inform)

  if len(groupSchedule) != 0:
    result = {"item": groupSchedule}
    return json.dumps(result, ensure_ascii=False)
  else:
    result = {"item": "no schedule exists"}
    return json.dumps(result)


@app.route('/schedule/<scheduleID>', methods=['POST', 'GET'])
def scheduleInfo(scheduleID):
  schedule = Schedule.query.filter_by(schedule_id=scheduleID).one_or_none()
  if schedule is None:
    result = {"error": "no schedule exist"}
    return json.dumps(result)
  result = {
    "schedule_id": schedule.schedule_id,
    "group_id": schedule.group_id,
    "name": schedule.name,
    "date": str(schedule.date)
  }
  return json.dumps(result, ensure_ascii=False)


@app.route('/schedule/modify/<scheduleID>', methods=['PUT', 'GET', 'POST'])
def modifySchedule(scheduleID):
  name = request.args.get("name")
  date = request.args.get("date")
  if name is None and date is None:
    result = {"modified": "false", "error": "wrong parameter"}
    return json.dumps(result)

  schedule = Schedule.query.filter_by(schedule_id=scheduleID).limit(1).first()
  if schedule is None:
    result = {"modified": "false", "error": "schedule not found"}
    return json.dumps(result)

  if name is None:
    name = schedule.name
  if date is None:
    date = schedule.date

  format = "%Y-%m-%d"
  date = datetime.strptime(date, format)

  schedule.date = date
  schedule.name = name
  try:
    db.session.commit()
    result = {"modified": "true"}
    return json.dumps(result)
  except:
    result = {"modified": "false"}
    return json.dumps(result)


@app.route('/schedule/delete/<scheduleID>', methods=['GET', 'DELETE'])
def deleteSchedule(scheduleID):
  schedule = Schedule.query.filter_by(
    schedule_id=scheduleID).limit(1).one_or_none()
  try:
    db.session.delete(schedule)
    db.session.commit()
    result = {"deleted": "true"}
    return json.dumps(result)
  except:
    result = {"deleted": "false"}
    return json.dumps(result)


@app.route('/notice/add', methods=['POST', 'GET'])
def addNotice():
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  id = rand(1000000000)
  id = str(id)
  valid = Notice.query.filter_by(notice_id=id).limit(1).one_or_none()
  while valid is not None:
    id = rand(1000000000)
    valid = Notice.query.filter_by(id=id).limit(1).one_or_none()

  groupID = request.args.get("group_id")
  name = request.args.get("name")
  content = request.args.get("content")

  if groupID is None or name is None or content is None:
    result = {"created": "false", "error": "wrong parameter"}
    return json.dumps(result)

  group = Group.query.filter_by(id=groupID).one_or_none()
  if group is None:
    result = {"registered": "false", "error": "no group exists"}
    return json.dumps(result)

  notice = Notice(id, groupID, name, content)
  try:
    db.session.add(notice)
    db.session.commit()
    result = {
      "registered": "true",
      "notice": {
        "notice_id": notice.notice_id,
        "group_id": notice.group_id,
        "name": notice.name,
        "content": notice.content
      }
    }
    return json.dumps(result, ensure_ascii=False)
  except:
    result = {"registered": "true", "error": "Fail to Add"}
    return json.dumps(result)


@app.route('/notice/user/<userID>', methods=['POST', 'GET'])
def userNotice(userID):
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  user = User.query.filter_by(id=userID).one_or_none()
  if user is None:
    result = {"error": "user not exists"}
    return json.dumps(result)

  groupList = select(Register_Info).join(User.register_infos)
  groupList = groupList.filter(Register_Info.user_id == int(userID))
  df = pd.read_sql(groupList, db.session.bind)
  if len(df) == 0:
    result = {"error": "notice not exists"}
    return json.dumps(result)

  groupSet = df["group_id"]
  print(groupSet)

  noticeList = []
  for groupID in groupSet:
    groupNotice = []
    notice = select(Notice).join(Group.notices)
    notice = notice.filter_by(group_id=int(groupID))
    df = pd.read_sql(notice, db.session.bind)
    for i in range(len(df)):
      inform = {
        "notice_id": str(df.notice_id[i]),
        "group_id": str(df.group_id[i]),
        "name": df.name[i],
        "content": str(df.content[i])
      }
      groupNotice.append(inform)
    if len(groupNotice) != 0:
      noticeList.append(groupNotice)
  print(noticeList)

  if len(noticeList) != 0:
    result = {"item": noticeList}
    return json.dumps(result, ensure_ascii=False)
  else:
    result = {"item": "no notice exists"}
    return json.dumps(result)


@app.route('/notice/group/<groupID>', methods=['POST', 'GET'])
def groupNotice(groupID):
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  groupNotice = []
  notice = select(Notice).join(Group.notices)
  notice = notice.filter_by(group_id=int(groupID))
  df = pd.read_sql(notice, db.session.bind)
  for i in range(len(df)):
    inform = {
      "notice_id": str(df.notice_id[i]),
      "group_id": str(df.group_id[i]),
      "name": df.name[i],
      "content": str(df.content[i])
    }
    groupNotice.append(inform)

  if len(groupNotice) != 0:
    result = {"item": groupNotice}
    return json.dumps(result, ensure_ascii=False)
  else:
    result = {"item": "no notice exists"}
    return json.dumps(result)


@app.route('/notice/<noticeID>', methods=['POST', 'GET'])
def noticeInfo(noticeID):
  notice = Notice.query.filter_by(notice_id=noticeID).one_or_none()
  if notice is None:
    result = {"error": "no notice exist"}
    return json.dumps(result)
  result = {
    "notice_id": notice.notice_id,
    "group_id": notice.group_id,
    "name": notice.name,
    "notice": notice.content
  }
  return json.dumps(result, ensure_ascii=False)


@app.route('/notice/modify/<noticeID>', methods=['POST', 'GET', 'PUT'])
def modifyNotice(noticeID):
  name = request.args.get("name")
  content = request.args.get("content")
  if name is None and content is None:
    result = {"modified": "false", "error": "wrong parameter"}
    return json.dumps(result)

  notice = Notice.query.filter_by(notice_id=noticeID).limit(1).first()
  if notice is None:
    result = {"modified": "false", "error": "notice not found"}
    return json.dumps(result)

  if name is None:
    name = notice.name
  if content is None:
    content = notice.content

  notice.content = content
  notice.name = name
  try:
    db.session.commit()
    result = {"modified": "true"}
    return json.dumps(result)
  except:
    result = {"modified": "false"}
    return json.dumps(result)


@app.route('/notice/delete/<noticeID>', methods=['DELETE', 'GET'])
def deleteNotice(noticeID):
  notice = Notice.query.filter_by(notice_id=noticeID).limit(1).one_or_none()
  try:
    db.session.delete(notice)
    db.session.commit()
    result = {"deleted": "true"}
    return json.dumps(result)
  except:
    result = {"deleted": "false"}
    return json.dumps(result)


@app.route('/user/modify/<userID>', methods=['POST', 'GET', 'PUT'])
def modifyUser(userID):
  email = request.args.get("email")
  name = request.args.get("name")
  pw = request.args.get("pw")

  if pw is not None:
    pw = str(hashlib.sha512(pw.encode()).hexdigest())

  if email is None and name is None and pw is None:
    result = {"modified": "false", "error": "wrong parameter"}
    return json.dumps(result)

  user = User.query.filter_by(id=userID).one_or_none()
  if user is None:
    result = {"modified": "false", "error": "user not found"}
    return json.dumps(result)

  if name is None:
    name = user.username
  if email is None:
    email = user.email
  if pw is None:
    pw = user.pw

  user.username = name
  user.email = email
  user.password = pw

  try:
    db.session.commit()
    result = {"modified": "true"}
    return json.dumps(result)
  except:
    result = {"modified": "false"}
    return json.dumps(result)


@app.route('/scanimage/<groupID>', methods=['POST', 'GET'])
def imageScan(groupID):
  api_url = os.environ['api_url']
  secret_key = os.environ['api_key']
  image_file = 'image.jpg'

  request_json = {
    'images': [{
      'format': 'jpg',
      'name': 'image'
    }],
    'requestId': str(uuid.uuid4()),
    'version': 'V2',
    'timestamp': int(round(time.time() * 1000))
  }

  payload = {'message': json.dumps(request_json).encode('UTF-8')}
  files = [('file', open(image_file, 'rb'))]
  headers = {'X-OCR-SECRET': secret_key}

  response = requests.request("POST",
                              api_url,
                              headers=headers,
                              data=payload,
                              files=files)

  result = response.text.encode('utf8')
  result = eval(result)['images'][0]['receipt']['result']

  moneydata_id = rand(1000000000)
  valid = MoneyList.query.filter_by(
    moneydata_id=moneydata_id).limit(1).one_or_none()
  while valid is not None:
    moneydata_id = rand(1000000000)
    valid = MoneyList.query.filter_by(
      moneydata_id=moneydata_id).limit(1).one_or_none()

  group_id = groupID

  try:
    if request.args.get("oneitem") == 'yes':
      name = result['storeInfo']['name']['text']
      try:
        name += ' ' + result['storeInfo']['subName']['text']
      except:
        pass

      date = result['paymentInfo']['date']['text']
      dateformat = "%Y-%m-%d"
      date = datetime.strptime(date, dateformat)
      value = int(result['totalPrice']['price']['formatted']['value'])
      data = MoneyList(moneydata_id=moneydata_id,
                       group_id=group_id,
                       name=name,
                       date=date,
                       value=value,
                  sval=getMoneyLast(group_id))
      db.session.add(data)
      db.session.commit()
      return json.dumps({"result": "true"})


    defname = result['storeInfo']['name']['text']
    try:
      defname += result['storeInfo']['subName']['text']
    except:
      pass
    date = result['paymentInfo']['date']['text']
    dateformat = "%Y-%m-%d"
    date = datetime.strptime(date, dateformat)
    for dataitem in result['subResults'][0]['items']:
      moneydata_id = rand(1000000000)
      valid = MoneyList.query.filter_by(
        moneydata_id=moneydata_id).limit(1).one_or_none()
      while valid is not None:
        moneydata_id = rand(1000000000)
        valid = MoneyList.query.filter_by(
          moneydata_id=moneydata_id).limit(1).one_or_none()
      name = defname + ' ' + dataitem['name']['text'] + ' ' + dataitem[
        'count']['text']
      value = int(dataitem['price']['price']['formatted']['value'])
      data = MoneyList(moneydata_id=moneydata_id,
                       group_id=int(group_id),
                       name=name,
                       date=date,
                       value=value,
            sval=getMoneyLast(group_id))
      db.session.add(data)
      db.session.commit()
      return json.dumps({"result": "true"})
  except Exception as e:
    print(e)
    return json.dumps({"result": "false"})


def getMoneyLast(groupID):
  last = MoneyList.query.filter_by(group_id=groupID).limit(1).one_or_none()

  if last is None:
    return 0
  return last.sval

@app.route('/moneylist/list', methods=['POST', 'GET'])
def getMoneyList():
  db.metadata.bind = 'sqlite:///data.db'
  db.session.configure(bind=db.metadata.bind)

  try:
    moneylist_set = select(MoneyList).join(Group.moneylists)
    moneylist_set = moneylist_set.filter(Group.id == int(request.args.get("group_id")))
    df = pd.read_sql(moneylist_set, db.session.bind)
    print(moneylist_set)
    return json.loads(df.to_json(force_ascii=False, orient='records'))
  except:
    return json.dumps({"result": False})


if (__name__ == '__main__'):
  random.seed()
  app.run(host='0.0.0.0')
