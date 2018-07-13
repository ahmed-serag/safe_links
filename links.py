import pymysql.cursors

class links():
    def __init__(self, database, username, password, port=3306):
        self.database=database
        self.username=username
        self.password=password
        self.port=port
    ####
    def addLink(self, platform, filename, current_link, packup_link, public_link, user):
        ## check if user exist return user ID else, add in db and return ID
        conn= pymysql.connect(
                host='localhost',  
                user=self.username, 
                password=self.password, 
                db=self.database,
                port=self.port,
                charset="utf8")
        cur = conn.cursor()

        cur.execute("""INSERT INTO `links`
                (`public_link`, `platform`, `file`, `current_link`, `packup_link`, `user`) 
                VALUES (%s, %s, %s, %s, %s, %s)""",(public_link, platform, filename, current_link, packup_link, user))
        conn.commit()
        cur.close() 
        conn.close()    
        
    ####
    def getLinks(self,public_link=None, platform=None, id=None):
        conn= pymysql.connect(
                host='localhost',  
                user=self.username, 
                password=self.password, 
                db=self.database,
                port=self.port,
                charset="utf8")
        cur = conn.cursor()
        if platform:
            cur.execute("SELECT * FROM `links` WHERE `platform`= %s ", (platform))
            link = cur.fetchall()
        elif id: 
            cur.execute("SELECT * FROM `links` WHERE `id` = %s", (id))
            link = cur.fetchall()
        elif public_link:
            cur.execute("SELECT * FROM `links` WHERE `public_link` = %s", (public_link))
            link = cur.fetchall()
        else:
            cur.execute("SELECT * FROM `links`")
            link = cur.fetchall()
        cur.close() 
        conn.close()
        if link:
            return link
    
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