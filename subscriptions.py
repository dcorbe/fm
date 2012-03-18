from DB import *
from topics import *
from post import *

class Subscription():

    querySubList = """
        SELECT *
        FROM subscriptions
        WHERE i_user = %s"""

    def __init__(self, i_user=None):
        self.id = 0
        self.i_user = 0
        self.threads = [ ]
        self.threadlist = [ ]

        if i_user:
            self.open(i_user)

    def open(self, i_user):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        db.execute(self.querySubList, (i_user))
        subs = db.fetchall()

        for row in subs:
            self.id = row[0];
            self.i_user = row[1];
    
            t = Topic(row[2]);
            self.threads.append(t)
            self.threadlist.append(row[2])
