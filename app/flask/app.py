from flask import Flask, request, render_template, flash, redirect, url_for, session, jsonify
from module import dbModule

app = Flask(__name__)

app.secret_key = 'TempMySessionKeywwwooososciuasdnsafdsf'

# 메인 페이지 
@app.route('/')
def index():
    return
    # if session:
    #     userId = session['userId']
    #     username = session['username']
    #     print(username)
    #     return render_template('index.html')
    # else:
    #     return render_template('index.html')

# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":

        # react 서버에서 아이디, 비밀번호 받아오기
        data = request.json
        userId = data.get('userId')
        userPw = data.get('userPw')

        cur = dbModule.Database().cursor # 커서 불러오기
        cur.execute("SELECT * FROM usertest WHERE signupUserId=%s AND signupUserPw=%s", (userId, userPw)) # 받아온 아이디, 비밀번호 정보와 일치하는 계정이 있는지 확인
        account = cur.fetchone() # sql 실행 결과 하나만 받아오기
        print(account==None)
        
        if account != None:
            session.clear()
            session['userId'] = account['signupUserId']
            session['username'] = account['username']
            session['logged_in'] = True
            cur.close()
            return jsonify({'message': '로그인에 성공했습니다.','username':account['username']}), 200
        else:
            return jsonify({'message': '아이디나 비밀번호가 옳지 않습니다.'}), 401

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    # return render_template('index.html')
    return redirect(url_for('index'))

# 회원가입
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        # react 서버에서 아이디, 비밀번호 받아오기
        data = request.json
        signupUserId = data.get('userId')
        signupUserPw = data.get('userPw')
        checkPw = data.get('checkPw')
        
        db = dbModule.Database() # 데이터 베이스(conn, cursor) 연결 객체
        cursor = db.cursor # 커서 생성
        
        cursor.execute('SELECT signupUserId FROM usertest WHERE signupUserId=%s', (signupUserId,))
        existingUserId = cursor.fetchone()

        if existingUserId is None and signupUserPw == checkPw:
            username = data.get('username')
            gender = data.get('gender')

            sql = "INSERT INTO usertest (signupUserId, signupUserPw, username, gender) values (%s, %s, %s, %s)"

            cursor.execute(sql, (signupUserId, signupUserPw, username, gender))
            db.conn.commit() # 실행한 SQL 문장 DB에 반영
            cursor.close() # 연결 닫기 
            db.conn.close() # 연결 닫기

            print(signupUserId, signupUserPw, checkPw, username, gender)
            return jsonify({'message': '회원가입이 완료되었습니다.'}), 200
        else:
            return jsonify({'message': '이미 존재하는 아이디이거나 비밀번호가 올바르지 않습니다.'}), 401
    else:
        return jsonify({'message': '회원가입 페이지 입니다.'})


# 로그인 체크(세션)
@app.route('/status')
def login_status():
    if session.get('logged_in'):
        return jsonify(logged_in=True, username=session.get('username')), 200
    else:
        return jsonify(logged_in=False), 200


if __name__ == '__main__':

    app.run(debug=True) # 실제 배포시 False로 변경
