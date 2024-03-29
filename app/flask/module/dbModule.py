import pymysql

class Database():
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', user='root', password='1791', db='mpdb', charset='utf8') # (1) MYSQL Connection 연결 (연결자 = pymysql.connect(연결옵션))
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor) # (2) 연결자로 부터 DB를 조작할 Cusor 생성 (커서이름 = 연결자.cursor())
        
        
