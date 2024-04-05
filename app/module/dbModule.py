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
        self.init_db()

    def init_db(self):
        # Connect to the database
        connection = pymysql.connect(
            host=DATABASE_HOST,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            db=DATABASE_DB,
        )
        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = """CREATE TABLE IF NOT EXISTS usertest (
                            userNum INT AUTO_INCREMENT PRIMARY KEY, 
                            userId VARCHAR(255) NOT NULL UNIQUE, 
                            userPw VARCHAR(255) NOT NULL,
                            userName VARCHAR(255),
                            userGender VARCHAR(255)
                        )"""
                cursor.execute(sql)

            # Connection is not autocommit by default. So you must commit to save your changes.
            connection.commit()
        finally:
            connection.close()
