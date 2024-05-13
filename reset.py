import os

os.system('rm -rf migrations')
os.system('rm data.db')

os.system('flask db init')  #migrate 폴더 생성 //처음 한번만 실
os.system('flask db migrate')  #스키마 읽어서 migrate
os.system('flask db upgrade')  #table 생성
