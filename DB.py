import MySQLdb
from config import *

class DB:
    """ This is basically a mysql_ping() hack, because MySQLdb unhelpfully lacks basic keepalive support """

    conn = None

    def __init__(self):
        self.Config = Config()

    def connect(self):
        #global conn
        self.conn = MySQLdb.connect(host = self.Config.database['host'],
                                    user = self.Config.database['user'],
                                    passwd = self.Config.database['pass'],
                                    db = self.Config.database['db'])
        #conn = self.conn
        self.conn.autocommit(True)

    def cursor(self):
        if self.conn:
            self.conn.ping(True)
        try:
            return self.conn.cursor()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            return self.conn.cursor()
        

    def getInstance():
        global conn
        
        if conn == None:
            conn = DB()
            
        return conn
