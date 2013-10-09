from DB import *

class Category():
    def __init__(self, i_category=0):
        self.id = 0
        self.name = None
        self.description = None

        self.open(i_category)

    def open(self, i_category):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        if i_category == 0:
            self.id = 0
            self.name = None
            self.description = None
            return

        db.execute(self.queryCategory, (i_category))
        category = db.fetchone()

        self.id = category[0]
        self.name = category[1]
        self.description = category[2]
