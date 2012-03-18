from DB import *
from topics import *
from post import *
import time

class Forum():
    def __init__(self, i_forum=None):
        self.id = None
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

