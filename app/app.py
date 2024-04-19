from flask import (
    Flask,
    request,
    render_template,
    flash,
    redirect,
    url_for,
    session,
    jsonify,
)
from module import dbModule, faceModule
import cv2
from module.crawlingModule import youtube
app = Flask(__name__)

app.secret_key = "TempMySessionKeywwwooososciuasdnsafdsf"


# 메인 페이지
@app.route("/")
def index():
    if session:
        userId = session["userId"]
        username = session["username"]
        print(username)
        return render_template("index.html")
    else:
        return render_template("loginorsignup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":  # 로그인 요청 일 경우
        # 변수에 html 폼에서 받아온 회원 아이디, 비밀번호 저장
        userId = request.form["userId"]
        userPw = request.form["userPw"]

        print(userId, userPw)
        # DB에 해당 계정 정보가 있는지 확인
        cursor = dbModule.Database().cursor
        cursor.execute(
            "SELECT * FROM userInfo WHERE userId = %s AND userPw = %s", (userId, userPw)
        )

        # 값의 유무 확인, 결과값 account변수에 넣기
        account = cursor.fetchone()
        print(account == None)

        if account != None:
            session.clear()
            session["userId"] = account["userId"]
            session["username"] = account["userName"]
            session['userAge'] = account['userAge']
            flash("로그인이 완료되었습니다.", "success")
            return redirect(url_for("index"))
        else:
            flash("아이디와 비밀번호를 다시 확인해주세요.", "danger")
            return render_template("login.html")
    else:
        if session:  # 세션이 있을 경우 (로그인 되어 있을 경우)
            return redirect(url_for("detail"))
        else:
            return render_template("login.html")

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

# 로그아웃
@app.route("/logout")
def logout():
    session.clear()
    # return render_template('index.html')
    return redirect(url_for("index"))


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
        image_url = url_for('static', filename=f'img/celeb/{result["Celeb"]}.jpg')
        session['celebImageUrl'] = image_url
        session['celebAnalysis'] = result

        return render_template('result.html', result = result, image_url=image_url)
    else:
        return render_template("similar_upload.html")

@app.route("/celeb_save", methods=["GET", "POST"])
def celeb_save():
    if request.method == "POST":
        celeb = session['celebAnalysis']
        celebImageUrl = session['celebImageUrl'] 
        userId = session['userId']

        cursor = dbModule.Database().cursor
        sql = 'INSERT INTO celeb_result (num, userId, celeb, probability) VALUES (0, %s, %s, %s)'
        cursor.execute(sql, (userId, celeb['Celeb'], celeb['Probability']))
        cursor.connection.commit()
        show_alert = True
        return render_template('result.html', result=celeb, show_alert = show_alert, image_url=celebImageUrl)
    else:
        del session['celebAnalysis']
        del session['celebImageUrl']
        
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

        gender_image_url = url_for('static', filename=f'img/gender/{gender_result["Gender"]}.png')
        race_image_url = url_for('static', filename=f'img/race/{race_result["race"]}.png')
        session['genderImageUrl'] = gender_image_url
        session['genderAnalysis'] = gender_result

        session['raceImageUrl'] = race_image_url
        session['raceAnalysis'] = race_result

        return render_template('feature_result.html', gender_result = gender_result, race_result=race_result, gender_image_url=gender_image_url, race_image_url=race_image_url)
    else:
        return render_template("feature_upload.html")
    
@app.route("/feature_save", methods=["GET", "POST"])
def feature_save():
    if request.method == "POST":
        gender = session['genderAnalysis']
        genderImageUrl = session['genderImageUrl'] 
        race = session['raceAnalysis']
        raceImageUrl = session['raceImageUrl']

        userId = session['userId']

        cursor = dbModule.Database().cursor
        sql = 'INSERT INTO feature_result (num, userId, gender, gender_probability, race, race_probability) VALUES (0, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (userId, gender['Gender'], gender['Probability'], race['race'], race['Probability']))
        cursor.connection.commit()
        show_alert = True
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

        age_image_url = url_for('static', filename=f'img/age/age.png')

        session['ageImageUrl'] = age_image_url
        session['ageAnalysis'] = age_result

        age = age_result['age'].split('~')
        print(age)
        print(range(int(age[0]), int(age[1])))
        
        msg = ''
        keyword = ''
        if int(session['userAge']) in range(int(age[0]), int(age[1])):
            # 나이에 맞을 경우
            keyword = '피부 나이 유지 방법'
        elif int(session['userAge']) < int(age[0]) or int(session['userAge']) < int(age[1]):
            # 노안일 경우
            keyword = '안티에이징'
        else:
            # 동안일 경우
            keyword = '성숙해보이는 메이크업'
    
        video_info = youtube(keyword)
        session['video_info'] = video_info

        return render_template('age_result.html', result = age_result, image_url=age_image_url, keyword=keyword)
    else:
        return render_template("age_upload.html")
    
@app.route("/age_save", methods=["GET", "POST"])
def age_save():
    if request.method == "POST":
        age = session['ageAnalysis']
        ageImageUrl = session['ageImageUrl'] 
        userId = session['userId']

        cursor = dbModule.Database().cursor
        sql = 'INSERT INTO age_result (num, userId, age, probability) VALUES (0, %s, %s, %s)'
        cursor.execute(sql, (userId, age['age'], age['Probability']))
        cursor.connection.commit()
        show_alert = True
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
        image_url = url_for('static', filename=f'img/animal/{result["animal"]}.jpg')
        session['animalImageUrl'] = image_url
        session['animalAnalysis'] = result

        return render_template('animal_result.html', result = result, image_url=image_url)
    else:
        return render_template("animal_upload.html")
    
@app.route("/animal_save", methods=["GET", "POST"])
def animal_save():
    if request.method == "POST":
        animal = session['animalAnalysis']
        animalImageUrl = session['animalImageUrl'] 
        userId = session['userId']

        cursor = dbModule.Database().cursor
        sql = 'INSERT INTO animal_result (num, userId, animal, probability) VALUES (0, %s, %s, %s)'
        cursor.execute(sql, (userId, animal['animal'], animal['Probability']))
        cursor.connection.commit()
        show_alert = True
        return render_template('animal_result.html', result=animal, show_alert = show_alert, image_url=animalImageUrl)
    else:
        del session['animalAnalysis']
        del session['animalImageUrl']
        
        return render_template("feature_upload.html")
#########################################################################################################################

@app.route('/history', methods=["GET", "POST"])
def history():
    param = request.args.get('param')
    if session:
        userId = session["userId"]
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
        session['h_info'] =h_info
        session['result'] = result
        return render_template("history.html", result=result, h_info=h_info[param], param=param)
    else:
        return redirect(url_for("login"))

@app.route('/del_history', methods=["GET", "POST"])
def del_history():
    param =request.args.get('param')
    num = request.args.get('num')
    print(param)

    userId = session["userId"]
    db = dbModule.Database()
    cursor = db.cursor
    sql = f"DELETE FROM {param}_result WHERE num = %s AND userId = %s"
    cursor.execute(sql, (num, userId))
    db.conn.commit()

    cursor.execute(f"SELECT * FROM {param}_result WHERE userId = %s", (userId))
    session['result'] = cursor.fetchall()
    return render_template("history.html", param=param, h_info=session['h_info'][param])


@app.route("/result", methods=["GET", "POST"])
def result():

    return render_template("animal_result.html")


if __name__ == "__main__":
    app.run(debug=True)  # 실제 배포시 False로 변경
