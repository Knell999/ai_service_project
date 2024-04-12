import pymysql

DATABASE_HOST = "localhost"
DATABASE_USER = "root"
DATABASE_PASSWORD = "1791"
DATABASE_DB = "ai_servicedb"


class Database:
    def __init__(self):
        self.conn = pymysql.connect(
            host=DATABASE_HOST,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            db=DATABASE_DB,
            charset="utf8",
        )  # (1) MYSQL Connection 연결 (연결자 = pymysql.connect(연결옵션))
        self.cursor = self.conn.cursor(
            pymysql.cursors.DictCursor
        )  # (2) 연결자로 부터 DB를 조작할 Cusor 생성 (커서이름 = 연결자.cursor())
    #     self.init_db()

    # def init_db(self):
    #     # Connect to the database
    #     connection = pymysql.connect(
    #         host=DATABASE_HOST,
    #         user=DATABASE_USER,
    #         password=DATABASE_PASSWORD,
    #         db=DATABASE_DB,
    #     )
    #     try:
    #         with connection.cursor() as cursor:
    #             # Create a new record
    #             sql = """CREATE TABLE IF NOT EXISTS userInfo (
    #                         num int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    #                         userId varchar(20) NOT NULL,
    #                         userPw varchar(20) NOT NULL,
    #                         userName varchar(8) NOT NULL,
    #                         userGender varchar(2) DEFAULT NULL,
    #                         signupTime timestamp NULL DEFAULT CURRENT_TIMESTAMP
    #                     );
                            
    #                     CREATE TABLE IF NOT EXISTS face_analysis_results (
    #                         num int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    #                         userId varchar(20) NOT NULL,
    #                         similar_face_result varchar(255) DEFAULT NULL,
    #                         similarity_percentage decimal(5,2) DEFAULT NULL,
    #                         gender_result varchar(255) DEFAULT NULL,
    #                         gender_percentage decimal(5,2) DEFAULT NULL,
    #                         created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    #                         CONSTRAINT fk_userId FOREIGN KEY (userId) REFERENCES userInfo(userId)
    #                     );"""
    #             cursor.execute(sql)

    #         # Connection is not autocommit by default. So you must commit to save your changes.
    #         connection.commit()
    #     finally:
    #         connection.close()
