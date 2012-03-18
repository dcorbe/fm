from DB import *

class User():

    queryUserSelect = """
        SELECT *
        FROM users
        WHERE id = %s"""

    def __init__(self, i_user=None):
        self.id = 0;
        self.username = None;
        self.password = None;

        if i_user:
            self.open(i_user)

    def open(self, i_user):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        db.execute(self.queryUserSelect, (i_user))
        row = db.fetchone()

        self.id = i_user
        self.username = row[1]
        self.password = row[2]
