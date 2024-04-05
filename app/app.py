from flask import Flask, request, render_template, flash, redirect, url_for, session, jsonify
from module import dbModule, faceModule
import cv2

app = Flask(__name__)

app.secret_key = 'TempMySessionKeywwwooososciuasdnsafdsf'


# 메인 페이지
@app.route('/')
def index():
    if session:
        userId = session['userId']
        username = session['username']
        print(username)
        return render_template('index.html')
    else:
        return render_template('index.html')


# # 로그인
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == "POST":

#         # react 서버에서 아이디, 비밀번호 받아오기
#         data = request.json
#         userId = data.get('userId')
#         userPw = data.get('userPw')

#         cur = dbModule.Database().cursor  # 커서 불러오기
#         cur.execute("SELECT * FROM userInfo WHERE userId=%s AND userPw=%s",
#                     (userId, userPw))  # 받아온 아이디, 비밀번호 정보와 일치하는 계정이 있는지 확인
#         account = cur.fetchone()  # sql 실행 결과 하나만 받아오기
#         print(account == None)

#         if account != None:
#             session.clear()
#             session['userId'] = account['userId']
#             session['username'] = account['userName']
#             session['logged_in'] = True
#             cur.close()
#             return jsonify({'message': '로그인에 성공했습니다.', 'username': account['userName']}), 200
#         else:
#             return jsonify({'message': '아이디나 비밀번호가 옳지 않습니다.'}), 401

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': # 로그인 요청 일 경우
        # 변수에 html 폼에서 받아온 회원 아이디, 비밀번호 저장
        userId = request.form['userId']
        userPw = request.form['userPw']

        print(userId, userPw)
        # DB에 해당 계정 정보가 있는지 확인
        cursor = dbModule.Database().cursor
        cursor.execute('SELECT * FROM userInfo WHERE userId = %s AND userPw = %s', (userId, userPw))

        # 값의 유무 확인, 결과값 account변수에 넣기
        account = cursor.fetchone()
        print(account == None)

        if account != None:
            session.clear()
            session['userId'] = account['userId']
            session['username'] = account['userName']
            flash('로그인이 완료되었습니다.', 'success')
            return redirect(url_for('index'))
        else:
            flash('아이디와 비밀번호를 다시 확인해주세요.', 'danger')
            return render_template('login.html')     
    else:
        if session: # 세션이 있을 경우 (로그인 되어 있을 경우)
            return render_template('detail.html')  
        else:
            return render_template('login.html')

@app.route('/similar_upload',methods=['GET', 'POST'])
def similar_upload():
    if request.method == "POST":    
        if 'image' not in request.files:
            return 'No file part'
        file = request.files['image']
        if file.filename == '':
            return 'No selected file'
        
        file_path = 'uploads/' + file.filename
        file.save(file_path)

        fa = faceModule.face_anlysis(file_path)
        result = fa.similar_face()
        # jsonify({'message': '파일 업로드 완료'})
        # 파일 업로드 성공을 응답으로 반환
        return result
    else:
        return render_template('similar_upload.html')

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    # return render_template('index.html')
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        signupUserId = request.form['userId']
        signupUserPw = request.form['userPw']
        checkPw = request.form['checkPw']
        
        db = dbModule.Database()
        cursor = db.cursor
        
        cursor.execute('SELECT userId FROM userInfo WHERE userId=%s', (signupUserId))
        existingUserId = cursor.fetchone()

        if existingUserId is None and signupUserPw == checkPw:
            username = request.form['username']
            userGender = request.form['userGender']

            sql = "INSERT INTO userInfo (num, userId, userPw, userName, userGender) values (0, %s, %s, %s, %s)"

            cursor.execute(sql, (signupUserId, signupUserPw, username, userGender))
            db.conn.commit()

            print(signupUserId, signupUserPw, checkPw, username, userGender)
            return redirect(url_for('index'))
        else:
            return render_template('signup.html')
    else:
        return render_template('signup.html')
# # 회원가입
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':

#         # react 서버에서 아이디, 비밀번호 받아오기
#         data = request.json
#         signupUserId = data.get('userId')
#         signupUserPw = data.get('userPw')
#         checkPw = data.get('checkPw')

#         db = dbModule.Database()  # 데이터 베이스(conn, cursor) 연결 객체
#         cursor = db.cursor  # 커서 생성

#         cursor.execute('SELECT userId FROM userInfo WHERE userId=%s', (signupUserId,))
#         existingUserId = cursor.fetchone()

#         if existingUserId is None and signupUserPw == checkPw:
#             username = data.get('username')
#             gender = data.get('gender')

#             sql = "INSERT INTO userInfo (num, userId, userPw, userName, userGender) values (0, %s, %s, %s, %s)"

#             cursor.execute(sql, (signupUserId, signupUserPw, username, gender))
#             db.conn.commit()  # 실행한 SQL 문장 DB에 반영
#             cursor.close()  # 연결 닫기
#             db.conn.close()  # 연결 닫기

#             print(signupUserId, signupUserPw, checkPw, username, gender)
#             return jsonify({'message': '회원가입이 완료되었습니다.'}), 200
#         else:
#             return jsonify({'message': '이미 존재하는 아이디이거나 비밀번호가 올바르지 않습니다.'}), 401
#     else:
#         return jsonify({'message': '회원가입 페이지 입니다.'})


# 로그인 체크(세션)
@app.route('/status')
def login_status():
    if session.get('logged_in'):
        return jsonify(logged_in=True, username=session.get('username')), 200
    else:
        return jsonify(logged_in=False), 200


if __name__ == '__main__':
    app.run(debug=True)  # 실제 배포시 False로 변경
