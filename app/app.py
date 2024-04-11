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
        return render_template("index.html")


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
            flash("로그인이 완료되었습니다.", "success")
            return redirect(url_for("index"))
        else:
            flash("아이디와 비밀번호를 다시 확인해주세요.", "danger")
            return render_template("login.html")
    else:
        if session:  # 세션이 있을 경우 (로그인 되어 있을 경우)
            return render_template("detail.html")
        else:
            return render_template("login.html")


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
            userGender = request.form["userGender"]

            sql = "INSERT INTO userInfo (num, userId, userPw, userName, userGender) values (0, %s, %s, %s, %s)"

            cursor.execute(sql, (signupUserId, signupUserPw, username, userGender))
            db.conn.commit()

            print(signupUserId, signupUserPw, checkPw, username, userGender)
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
        # jsonify({'message': '파일 업로드 완료'})
        # 파일 업로드 성공을 응답으로 반환
        return result
    else:
        return render_template("similar_upload.html")


@app.route("/detail")
def detail():
    if session:
        userId = session["userId"]
        cursor = dbModule.Database().cursor
        cursor.execute(
            "SELECT * FROM face_analysis_results WHERE userId = %s", (userId)
        )
        result = cursor.fetchall()
        return render_template("detail.html", result=result)
    else:
        return redirect(url_for("login"))


@app.route("/result", methods=["GET"])
def result():
    return render_template("result.html")


@app.route("/history")
def history(id):
    return "wow such history much wow " + id


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


if __name__ == "__main__":
    app.run(debug=True)  # 실제 배포시 False로 변경
