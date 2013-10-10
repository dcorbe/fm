from DB import *
from topics import *
from post import *
import time

class Forum():

    queryForumSelect = """
        SELECT id
        FROM threads
        WHERE i_forum = %s
        ORDER BY bumped DESC
    """
    
    queryByShortname = """
        SELECT id, name, description, shortname
        FROM forums
        WHERE shortname = %s
    """

    def __init__(self, i_forum=None):
        self.id = 0
        self.threads = [ ]
        self.ts = 0
        self.threadcount = 0
        self.name = None
        self.description = None
        self.shortname = None
        self.lastpost = None
        self.lastthread = None

        if i_forum:
            self.open(i_forum)

    def open(self, i_forum):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        if not i_forum:
            return

        self.id = int(i_forum)

        db.execute(self.queryForumSelect, (self.id))
        rows = db.fetchall()

        for row in rows:
            thread = Topic(row[0])
            self.threadcount = self.threadcount + 1
            self.threads.append(thread)
            
    def byshortname(self, string):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()
            
        db.execute(self.queryByShortname, (string))
        row = db.fetchone()

        self.id = int(row[0])
        self.name = row[1]
        self.description = row[2]
        self.shortname = row[3]
