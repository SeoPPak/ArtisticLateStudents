from app import db, render_template, request
from flask import redirect, url_for
from app import User, Group, Schedule, Notice, Register_Info, InviteCode
import app
import hashlib

app = app.create_app()
@app.route('/list')
def getList():
    user_list = User.query.all()
    # user_list에 Member의 모든 튜플 저장

    if (type(user_list) != type([])):
        user_list = [user_list]

    return render_template('user_list.html', user_list=user_list)


@app.route('/user/<user_id>')
def getgrouplist(user_id):
    grouplist = Register_Info.query.filter_by(user_id=user_id)
    if (type(grouplist) != type([])):
        grouplist = [grouplist]

    return render_template('group_list.html', group_list=grouplist)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        id = request.form['id']

        user = User.query.filter_by(id=id).first()
        if user:
            return '{result: "중복된 아이디가 있습니다."}', 406

        password = request.form['pw']
        username = request.form['name']
        email = request.form['email']

        user = User.query.filter_by(email=email).first()
        if user:
            return '{result: "이미 가입된 이메일입니다."}', 406

        user = User(id, password, username, email)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("getList"))
    else:
        return render_template('signup.html')

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pw = request.form['pw']
        pw = str(hashlib.sha512(pw.encode()).hexdigest())

        user = User.query.filter_by(email=email).first()
        if user is not None:
            id = user.id
            return redirect(url_for('getgrouplist', user_id=id))
        else:
            return redirect(url_for('register'))
    else:
        return render_template('login.html')


if (__name__ == '__main__'):
    app.run(host='0.0.0.0')
