from flask import Flask, render_template, \
    request, redirect, url_for, session, jsonify, make_response, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import jwt
from datetime import datetime, timedelta
from functools import wraps
import time

app = Flask(__name__)

# app.secret_key = 'kraftonjungle'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mslee0702'
app.config['MYSQL_DB'] = 'jungleground'
app.config['SECRET_KEY'] = 'kraftonjungle'
# According to Flask-JWT-Extended docs SECRET_KEY is used for JWTs
# instead if JWT_SECRET_KEY is not defined
# 참조 링크 : https://flask-jwt-extended.readthedocs.io/en/stable/options/#JWT_SECRET_KEY

mysql = MySQL(app)

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs) :
        token = request.args.get('token')
        if not token:
            return jsonify({'token' : 'token is missing'})
        try:
            payload = jwt.decode(token,app.config['SECRET_KEY'])
        except:
            return jsonify({'alert':'invalid token'})
    return decorated

@app.route('/public')
def public():
    return 'for public'

@app.route('/auth')
@token_required
def auth():
    return 'jwt is verified'

@app.route('/')

# 로그인
@app.route('/login', methods =['GET', 'POST'])
def login():
    auth = request.authorization
    msg = ''
    if request.method == 'POST' and 'phone' in request.form and 'password' in request.form:
        phone = request.form['phone']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE phone = % s AND password = % s', (phone, password, ))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['phone'] = account['phone']
            session['username'] = account['username']
            token = jwt.encode({
                'user':request.form['phone'],
                'expiration': str(datetime.utcnow() + timedelta(seconds=120))
            },
                app.config['SECRET_KEY'])
            # return jsonify({'token':token.decode('utf-8')})
            # 파이썬3에서는 기본으로 UTF-8 인코딩 이기 때문에 굳이 디코드 해 줄 필요 없음 디코드시 (TypeError: 'str' object is not callable) 나옴
            # return jsonify({'token':token})
            # 토큰 유효성 확인 위한 디버깅 코드(https://jwt.io)에서 확인

            msg = '성공적으로 로그인 되었습니다!'

            return redirect(url_for('main'))
        else:
            msg = '휴대폰 번호 / 비밀번호가 일치하지 않습니다!'
    return render_template('login.html', msg = msg)

# 로그아웃
@app.route('/logout')
def logout():
    # session.pop('loggedin', None)
    # session.pop('id', None)
    # session.pop('phone', None)
    session.clear()
    # 모든 세선 한번에 클리어
    return redirect(url_for('login'))

# 회원가입
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'phone' in request.form and 'email' in request.form and 'password' in request.form :
        phone = request.form['phone']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE phone = % s', (phone, ))
        account = cursor.fetchone()
        if account:
            msg = '이미 존재하는 전화번호 입니다!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = '이메일 형식이 아닙니다!'
        # elif not re.match(r'[0-9]+', phone):
        elif not re.match(r'^010-[0-9]{4}-[0-9]{4}$', phone):
            msg = '휴대폰 번호는 010-XXXX-XXXX 형식으로 입력해주세요!'
        elif not phone or not password or not email:
            msg = '양식에 맞게 입력해 주세요!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s ,%s)', (phone, username, email, password, 0))
            mysql.connection.commit()

            msg = '성공적으로 가입되었습니다!'


    elif request.method == 'POST':
        msg = '모든 항목을 기입해 주세요!'
    return render_template('register.html', msg = msg)

# 메모 서버에 저장 기능
@app.route('/memo', methods = ['GET','POST'])
def memo():
    if request.method == 'POST':
        memos = request.form.get('memo')
        ad = '1'

        now_time = time.time()
        offset = datetime.fromtimestamp(now_time) - datetime.utcfromtimestamp(now_time)
        utc_time = round(datetime.utcnow().timestamp() * 1000)
        realtime = datetime.fromtimestamp(int(utc_time) / 1000) + offset

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE id={}".format(session['id']))
        team = cursor.fetchall()
        cursor.execute("INSERT INTO memos VALUES (NULL, 1, %s, %s, %s, %s)", (session['username'], memos, realtime.strftime('%Y-%m-%d %H:%M:%S'),team[0]['team']))
        mysql.connection.commit()

        return redirect(url_for('memo'))
    else:
        return redirect(url_for('make'))

# 메모 생성 기능
@app.route('/make')
def make():
    # ad = '1' -> 고정되지 않은 메모
    # ad2 = '0' -> 고정된 메모
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 팀 메모 기능
    cursor.execute("SELECT * FROM accounts WHERE id={}".format(session['id']))
    team = cursor.fetchall()
    # print(team[0]['team'])

    if team[0]['team'] == 0:
        cursor.execute("SELECT * FROM memos WHERE ad=1 AND username='{}'".format(team[0]['username']))
        datas = cursor.fetchall()
        cursor.execute("SELECT * FROM memos WHERE ad=0 AND username='{}'".format(team[0]['username']))
        ad_datas = cursor.fetchall()
        return render_template('memo.html', datas=list(datas), ad_datas=list(ad_datas))
    else:
        cursor.execute("SELECT * FROM memos WHERE ad=1 AND team={}".format(team[0]['team']))
        datas = cursor.fetchall()
        cursor.execute("SELECT * FROM memos WHERE ad=0 AND team={}".format(team[0]['team']))
        ad_datas = cursor.fetchall()
        cursor.execute("SELECT * FROM accounts WHERE team={}".format(team[0]['team']))
        team_mate = cursor.fetchall()
        return render_template('memo.html', datas=list(datas), ad_datas=list(ad_datas), team_mate=list(team_mate))
    # cursor.execute('SELECT * FROM memos WHERE ad = 1')
    # datas = cursor.fetchall()
    # cursor.execute('SELECT * FROM memos WHERE ad = 0')
    # ad_datas = cursor.fetchall()
    # return render_template('memo.html', datas=list(datas), ad_datas=list(ad_datas))


#메모 삭제 기능
@app.route('/del')
def delete():
    name = request.args.get('name')
    id = request.args.get('id')

    if name == session['username']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM memos WHERE id = {}".format(int(id)))
        mysql.connection.commit()
        return redirect(url_for('make'))
    else:
        flash('삭제 권한이 없습니다!')
        return redirect(url_for('make'))

# 메모 고정 기능
@app.route('/fix')
def fix():
    name = request.args.get('name')
    ad = request.args.get('ad')
    id = request.args.get('id')

    if name == session['username']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if ad == '1':
            cursor.execute("UPDATE memos SET ad=0 WHERE id={}".format(int(id)))
            mysql.connection.commit()
            return redirect(url_for('make'))
        else:
            cursor.execute("UPDATE memos SET ad=1 WHERE id={}".format(int(id)))
            mysql.connection.commit()
            return redirect(url_for('make'))
    else:
        flash('수정 권한이 없습니다!')
        return redirect(url_for('make'))


cnt = 1
@app.route('/serch', methods=['GET','POST'])
def serch():
    global cnt
    if request.method == 'POST':
        # 추가 팀원 데이터
        name = request.form.get('name')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE username='{}'".format(name))
        check = cursor.fetchall()

        if check:
            cursor.execute("SELECT * FROM accounts WHERE id={}".format(session['id']))
            inviter = cursor.fetchall()
            inviter_name = inviter[0]['username']
            inviter_num = inviter[0]['team']

            if inviter_num == 0:
                cursor.execute("UPDATE memos SET team={} WHERE username='{}'".format(cnt,inviter_name))
                cursor.execute("UPDATE accounts SET team={} WHERE username='{}'".format(cnt,inviter_name))
                cursor.execute("UPDATE memos SET team={} WHERE username='{}'".format(cnt,name))
                cursor.execute("UPDATE accounts SET team={} WHERE username='{}'".format(cnt,name))
                mysql.connection.commit()
                cnt += 1
                return redirect(url_for('make'))
            else:
                cursor.execute("UPDATE memos SET team={} WHERE username='{}'".format(inviter_num,name))
                cursor.execute("UPDATE accounts SET team={} WHERE username='{}'".format(inviter_num,name))
                mysql.connection.commit()
                cnt += 1
                return redirect(url_for('make'))
        else:
            flash("해당 가입자가 존재하지 않습니다.")
            return redirect(url_for('make'))


@app.route('/main')
def main():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM accounts WHERE id={}".format(session['id']))
    team = cursor.fetchall()

    cursor.execute("SELECT * FROM timeline ORDER BY date asc")
    task_datas = cursor.fetchall()

    if team[0]['team'] == 0:
        return render_template('index.html', task_datas = list(task_datas))
    else:
        cursor.execute("SELECT * FROM accounts WHERE team={}".format(team[0]['team']))
        team_mate = cursor.fetchall()
        return render_template('index.html', datas=list(team_mate), task_datas = list(task_datas))

@app.route('/del_member')
def del_member():
    name = request.args.get('name')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE memos SET team={} WHERE username='{}'".format(0,name))
    cursor.execute("UPDATE accounts SET team={} WHERE username='{}'".format(0,name))
    mysql.connection.commit()
    return redirect(url_for('make'))