'''
import os

os.system('set FLASK_APP=app')
os.system('set FLASK_DEBUG=true')
os.system('flask run')
'''

import Database as db

#DB에 테이블 생성
db.Base.metadata.create_all(db.engine)

#객체 생성
id_in = str(input("id : "))
pwd_in = str(input("password : "))
username_in = str(input("username : "))
email_in = str(input("email : "))
            
user1 = db.user.User(id=id_in,
             password=pwd_in,
             username=username_in,
             email=email_in,
             grouplist='')

#Session에 올림
db.session.add(user1)
#DB에 올림
db.session.commit()
