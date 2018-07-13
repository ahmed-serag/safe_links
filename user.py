import pymysql.cursors

class user():
    def __init__(self, database, username, password, port=3306):
        self.database=database
        self.username=username
        self.password=password
        self.port=port
    ####
    def addUser(self, username, password, type):
        ## check if user exist return user ID else, add in db and return ID
        conn= pymysql.connect(
                host='localhost',  
                user=self.username, 
                password=self.password, 
                db=self.database,
                port=self.port,
                charset="utf8")
        cur = conn.cursor()

        cur.execute("SELECT * FROM `user` WHERE `username` = %s", (username))
        user = cur.fetchone()
        if not user:
            cur.execute("""INSERT INTO `user`
                    (`username`, `password`, `type`) 
                    VALUES (%s, %s, %s)""",(username, password, type))
            conn.commit()
            cur.execute("SELECT LAST_INSERT_ID()")
            user = cur.fetchone()
            cur.execute("SELECT * FROM `user` WHERE `id` = %s", (user[0]))
            user = cur.fetchone()
        cur.close() 
        conn.close()    
        return user
    ####
    def getUser(self, id=None, type=None, username=None):
        conn= pymysql.connect(
                host='localhost',  
                user=self.username, 
                password=self.password, 
                db=self.database,
                port=self.port,
                charset="utf8")
        cur = conn.cursor()
        if type:
            cur.execute("SELECT * FROM `user` WHERE `type`= %s ", (type))
            user = cur.fetchall()
        elif id: 
            cur.execute("SELECT * FROM `user` WHERE `id` = %s", (id))
            user = cur.fetchall()
        elif mail:
            cur.execute("SELECT * FROM `user` WHERE `username` = %s", (username))
            user = cur.fetchall()
        cur.close() 
        conn.close()
        if user:
            return user
        else:
            return None
    ####    
    def login(self, password, mail=None, username=None):
        if mail:
            conn= pymysql.connect(
                host='localhost',  
                user=self.username, 
                password=self.password, 
                db=self.database,
                port=self.port,
                charset="utf8")
            cur = conn.cursor()
            cur.execute("SELECT * FROM `user` WHERE `mail` = %s AND `password` = %s", (mail,password))
            user = cur.fetchone()
            cur.close() 
            conn.close()
            return user
        elif username:
            conn= pymysql.connect(
                host='localhost',  
                user=self.username, 
                password=self.password, 
                db=self.database,
                port=self.port,
                charset="utf8")
            cur = conn.cursor()
            cur.execute("SELECT * FROM `user` WHERE `username` = %s AND `password` = %s", (username,password))
            user = cur.fetchone()
            cur.close() 
            conn.close()
            return user
        return None
    ####