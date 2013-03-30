import hashlib
from DB import *

class User():

    queryUserSelect = """
        SELECT id_member,member_name,passwd
        FROM hamsterdam.smf_members
        WHERE id_member = %s"""

    queryUnameSelect = """
	SELECT id_member,member_name,passwd
	FROM hamsterdam.smf_members
	WHERE member_name = %s"""

    queryUidSelect = """
	SELECT member_name
	FROM hamsterdam.smf_members
	WHERE id_member = %s"""

    def __init__(self, i_user=0):
        self.id = 0;
        self.username = None;
        self.password = None;

        self.open(i_user)

    def open(self, i_user):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        # Special case
        if i_user == 0:
            self.id = 0
            self.username = 'Random'
            self.password = ''
            return

        db.execute(self.queryUserSelect, (i_user))
        row = db.fetchone()

        self.id = i_user
        self.username = row[1]
        self.password = row[2]

    def get_user(self, username):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        db.execute(self.queryUnameSelect, (username))
        row = db.fetchone()

        self.id = row[0]
        self.username = row[1]
        self.password = row[2]

    def passcomp(self, password):
        hashpass = hashlib.sha1(self.username.lower() + password)

        print "<h1> COMPARING: {0} TO: {1}".format(hashpass.hexdigest(), self.password)

        if hashpass.hexdigest() == self.password:
            return True
        
        return False
