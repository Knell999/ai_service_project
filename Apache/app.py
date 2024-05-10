from flask import (Flask, request, render_template, flash, redirect, url_for, session, jsonify)
from module import dbModule
from module import faceModule
from flask_cors import CORS

# import cv2
from module.crawlingModule import youtube
app = Flask(__name__)
app.secret_key = "TempMySessionKeyYeah"
# app.config['SESSION_COOKIE_SAMESITE'] = 'None'

CORS(app, supports_credentials=True)

# 메인 페이지
@app.route("/")
def index():
    if session.get('logged_in') == True:
        return f"로그인 상태는 {session['logged_in']}입니다. 로그인 아이디: {session['userId']}, 성별 {session['userAge']}"
    else:
        return "로그인되어 있지 않습니다."
    
@app.route("/get_userdata")
def get_username():

    return jsonify({"userId": session['userId'], "username": session['username']})
# 로그인
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        session['test'] = 'POST 요청까지는 세션 작동함을 의미'
        data = request.get_json()
        print(data)
        userId = data['userId']
        userPw = data['userPw']

        cursor = dbModule.Database().cursor # 커서 생성
        sql = 'SELECT * FROM userInfo WHERE userId = %s AND userPw = %s'
        cursor.execute(sql, (userId, userPw)) # sql 실행
        account = cursor.fetchone() # sql 실행 결과 1개 가져오기
        print(account)
        print(account == None)

        if account != None:
            session.clear()
            session['logged_in'] = True
            session["userId"] = account["userId"]
            session["username"] = account["userName"]
            session["userAge"] = account["userAge"]
            session['createdAt'] = account['signupTime']
            print(session["userAge"])
            return {'success': True, 'session': session}
        else:
            return '로그인 실패'
    else:
        print('get')
        # email = request.args.get('email')
        # password = request.args.get('password')

        # if email and password:
        #     if email == 'abc' and password == '123':
        #         return "ok"
        #     else:
        #         return "fail"
        #session['userId'] = 'GET 요청까지는 세션 작동함을 의미'
        return 'GET'
@app.route("/uploadProfile", methods = ["POST"])
def uploadProfile():
    image_file = request.files['profileImage']
    print(image_file.filename)
    if image_file.filename == '':
        print('이미지 없음')
        return jsonify({'success':False, 'msg': '이미지가 선택되지 않았습니다.'})
    else:            
        image_file.save('uploads/' + session['userId']+'.jpg')
        print('이미지 있음')
        return {'success': True, 'img':f'uploads/{session["userId"]}.jpg'}
# 로그아웃
@app.route("/logout")
def logout():
    session.clear()
    print('세션 제거 완료')
    return {'success':True}

@app.route("/detail")
def detail():
    if session:
        userId = session["userId"]
        cursor = dbModule.Database().cursor
        cursor.execute(
            "SELECT * FROM userInfo WHERE userId = %s", (userId)
        )
        result = cursor.fetchone()
        session['signupTime'] = result['signupTime']
        return render_template("detail.html", result=result)
    else:
        return redirect(url_for("login"))

# @app.route("/history")
# def history(id):
#     return "wow such history much wow " + id

@app.route("/delete_hist")
def delete_hist(num):
    userId = session["userId"]
    cursor = dbModule.Database().cursor
    cursor.execute(
        "DELETE FROM face_analysis_results WHERE userId = %s AND num = %s",
        (userId, num),
    )
    dbModule.Database().conn.commit()
    return redirect(url_for("detail"))




@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        signupUserId = request.form["userId"]
        signupUserPw = request.form["userPw"]
        checkPw = request.form["checkPw"]

        db = dbModule.Database()
        cursor = db.cursor

        cursor.execute("SELECT userId FROM userInfo WHERE userId=%s", (signupUserId))
        existingUserId = cursor.fetchone()

        if existingUserId is None and signupUserPw == checkPw:
            username = request.form["username"]
            userAge = request.form['userAge']
            userGender = request.form["userGender"]

            sql = "INSERT INTO userInfo (num, userId, userPw, userName, userAge, userGender) values (0, %s, %s, %s, %s, %s)"

            cursor.execute(sql, (signupUserId, signupUserPw, username, userAge, userGender))
            db.conn.commit()

            print(signupUserId, signupUserPw, checkPw, username, userAge, userGender)
            return redirect(url_for("index"))
        else:
            return render_template("signup.html")
    else:
        return render_template("signup.html")


@app.route("/similar_upload", methods=["GET", "POST"])
def similar_upload():
    if request.method == "POST":
        if "image" not in request.files:
            return "No file part"
        file = request.files["image"]
        if file.filename == "":
            return "No selected file"

        file_path = "uploads/" + file.filename
        file.save(file_path)

        fa = faceModule.face_anlysis(file_path)
        result = fa.similar_face()
        image_url = f'img/celeb/{list(result.keys())[0]}.jpg'

        # session['celebImageUrl'] = image_url
        # session['celebAnalysis'] = result

        print(result)
        return {'data': result, 'img':image_url}
    else:
        return 'ㅎㅎ'

@app.route("/celeb_save", methods=["GET", "POST"])
def celeb_save():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        userId = session['userId']
        dataKey = list(data['data'].keys())[0]
        dataValue = data['data'][dataKey]
        print(dataKey, dataValue)
        cursor = dbModule.Database().cursor
        sql = 'INSERT INTO celeb_result (num, userId, celeb, probability) VALUES (0, %s, %s, %s)'
        cursor.execute(sql, (userId, dataKey, dataValue))
        cursor.connection.commit()

        return {'success':True}
    else:
        del session['celebAnalysis']
        del session['celebImageUrl']
        return {'success':False}
        
        return render_template("similar_upload.html")
#########################################################################################################################
@app.route("/feature_upload", methods=["GET", "POST"])
def feature_upload():
    if request.method == "POST":
        if "image" not in request.files:
            return "No file part"
        file = request.files["image"]
        if file.filename == "":
            return "No selected file"

        file_path = "uploads/" + file.filename
        file.save(file_path)

        fa = faceModule.face_anlysis(file_path)
        gender_result = fa.gender_detector()
        race_result = fa.race_detector()

        gender_image_url = f'img/gender/{gender_result["Gender"]}.png'
        race_image_url = f'img/race/{race_result["race"]}.png'
        image_url = {'gender':gender_image_url, 'race':race_image_url}

        return {'gender_result':gender_result, 'race_result':race_result, 'img':image_url}
    else:
        return 'hi'
    
@app.route("/feature_save", methods=["GET", "POST"])
def feature_save():
    if request.method == "POST":
        data = request.get_json()

        userId = session['userId']
        dataKey = data['gender_result']['Gender']
        dataValue = data['gender_result']['Probability']

        dataKey = data['race_result']['race']
        dataValue = data['race_result']['Probability']

        print(dataKey, dataKey)

        cursor = dbModule.Database().cursor
        sql = 'INSERT INTO feature_result (num, userId, gender, gender_probability, race, race_probability) VALUES (0, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (userId, dataKey, dataValue, dataKey, dataValue))
        cursor.connection.commit()
        
        return {'success':True}
        return render_template('feature_result.html', gender_result=gender, race_result=race, show_alert = show_alert, gender_image_url=genderImageUrl, race_image_url=raceImageUrl)
    else:
        del session['genderAnalysis']
        del session['genderImageUrl']
        
        return render_template("feature_upload.html")
#########################################################################################################################
@app.route("/age_upload", methods=["GET", "POST"])
def age_upload():
    if request.method == "POST":
      
        if "image" not in request.files:
            return "No file part"
        file = request.files["image"]
        if file.filename == "":
            return "No selected file"

        file_path = "uploads/" + file.filename
        file.save(file_path)
        
        fa = faceModule.face_anlysis(file_path)
        age_result = fa.age_detector()

        image_url = f'img/age/age.png'
        userAge = int(request.form['userAge'])

        age = age_result['age'].split('~')
        print(age)
        print(range(int(age[0]), int(age[1])))

        

        msg = ''
        keyword = ''
        if userAge in range(int(age[0]), int(age[1])):
            # 나이에 맞을 경우
            keyword = '피부 나이 유지 방법'
        elif userAge < int(age[0]) or int(session['userAge']) < int(age[1]):
            # 노안일 경우
            keyword = '안티에이징'
        else:
            # 동안일 경우
            keyword = '성숙해보이는 메이크업'
    
        video_info = youtube(keyword)
        session['video_info'] = video_info

        return {'data': age_result, 'img':image_url, 'session':session, 'keyword':keyword}
        return render_template('age_result.html', result = age_result, image_url=age_image_url, keyword=keyword)
    else:
        return 'ㅗㅗ'
    
@app.route("/age_save", methods=["GET", "POST"])
def age_save():
    if request.method == "POST":
        data = request.get_json()
        userId = session['userId']
        dataKey = data['data']['age']
        dataValue = data['data']['Probability']

        cursor = dbModule.Database().cursor
        sql = 'INSERT INTO age_result (num, userId, age, probability) VALUES (0, %s, %s, %s)'
        cursor.execute(sql, (userId, dataKey, dataValue))
        cursor.connection.commit()
        
        return {'success':True, 'session':session}
        return render_template('age_result.html', result=age, show_alert = show_alert, image_url=ageImageUrl )
    else:
        del session['ageAnalysis']
        del session['ageImageUrl']
        del session['video_info']
        
        return render_template("age_upload.html")
#########################################################################################################################
@app.route("/animal_upload", methods=["GET", "POST"])
def animal_upload():
    if request.method == "POST":
        if "image" not in request.files:
            return "No file part"
        file = request.files["image"]
        if file.filename == "":
            return "No selected file"

        file_path = "uploads/" + file.filename
        file.save(file_path)

        fa = faceModule.face_anlysis(file_path)
        result = fa.animal_detector()
    
        image_url = f'img/animal/{result["animal"]}.jpg'

        session['animalImageUrl'] = image_url
        session['animalAnalysis'] = result

        return {'data':result, 'img':image_url }
        return render_template('animal_result.html', result = result, image_url=image_url)
    else:
        return render_template("animal_upload.html")
    
@app.route("/animal_save", methods=["GET", "POST"])
def animal_save():
    if request.method == "POST":
        data = request.get_json()
        userId = session['userId']
        
        dataKey = data['data']['animal']
        dataValue = data['data']['Probability']

        cursor = dbModule.Database().cursor
        sql = 'INSERT INTO animal_result (num, userId, animal, probability) VALUES (0, %s, %s, %s)'
        cursor.execute(sql, (userId, dataKey, dataValue))
        cursor.connection.commit()
        
        return {'success':True}
    else:
        del session['animalAnalysis']
        del session['animalImageUrl']
        
        return render_template("feature_upload.html")
#########################################################################################################################

@app.route('/history', methods=["GET", "POST"])
def history():
    if session:
        param = request.get_json()['param']
        print(param)
        userId = session["userId"]
        print(userId)
        cursor = dbModule.Database().cursor
        cursor.execute(
            f"SELECT * FROM {param}_result WHERE userId = %s", (userId)
        )
        result = cursor.fetchall()

        s = ['닮은 꼴 연예인', '유사한 얼굴', '유사도']
        am = ['닮은 동물상', '닮은 동물', '유사도']
        a = ['노안도', '예상 나이', '확률']
        f = ['얼굴 특징', '성별', '성별 확률', '인종', '유사도']
        h_info = {'celeb':s, 'animal': am, 'age':a, 'feature':f}
        h_info = h_info[param]
        # session['h_info'] = h_info[param]
        session['result'] = result

        return {'success':True, 'result':result, 'h_info':h_info, 'param':param}
        return render_template("history.html", result=result, h_info=h_info[param], param=param)
    else:
        return redirect(url_for("login"))

@app.route('/del_history', methods=["GET", "POST"])
def del_history():
    data = request.get_json()
    param = data['param']
    num = data['num']
    print(param, num)

    userId = session["userId"]
    db = dbModule.Database()
    cursor = db.cursor
    sql = f"DELETE FROM {param}_result WHERE num = %s AND userId = %s"
    cursor.execute(sql, (num, userId))
    db.conn.commit()

    cursor.execute(f"SELECT * FROM {param}_result WHERE userId = %s", (userId))
    session['result'] = cursor.fetchall()
    return {'success':True}
    return render_template("history.html", param=param, h_info=session['h_info'][param])


@app.route("/result", methods=["GET", "POST"])
def result():

    return render_template("animal_result.html")


if __name__ == "__main__":
    app.run(debug=True)  # 실제 배포시 False로 변경
