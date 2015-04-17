import hashlib
from DB import *
from config import *

class User():

    queryUserSelect = """
        SELECT *
        FROM users
        WHERE id = %s"""
    querySMFUserSelect = """
        SELECT id_member,member_name,passwd
        FROM hamsterdam.smf_members
        WHERE id_member = %s"""

    queryUnameSelect = """
        SELECT id,username,password
        FROM users
        WHERE username = %s"""
    querySMFUnameSelect = """
	SELECT id_member,member_name,passwd
	FROM hamsterdam.smf_members
	WHERE member_name = %s"""

    queryUidSelect = """
        SELECT id,username,password
        FROM users
        WHERE username = %s"""
    querySMFUidSelect = """
	SELECT member_name
	FROM hamsterdam.smf_members
	WHERE id_member = %s"""


    def __init__(self, i_user=0, config=None):
        self.id = 0;
        self.username = None;
        self.password = None;
        self.Config = None;

        if config:
            self.Config = config
        else:
            self.Config = Config()

        self.open(i_user)

    def open(self, i_user):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        # Special case, used by playlist (amongst other things)
        if i_user == 0:
            self.id = 0
            self.username = 'Random'
            self.password = ''
            return

        if self.Config.user['backend'] == 'mysql':
            db.execute(self.queryUserSelect, (i_user))
        elif self.Config.user['backend'] == 'simplemachines':
            db.execute(self.querySMFUserSelect, (i_user))
        else:
            # TODO: Throw an exception here, but I don't know how to do that
            #       at the moment :(
            pass
            
        row = db.fetchone()

        try:
            self.id = i_user
            self.username = row[1]
            self.password = row[2]
        except:
            self.id = 0
            self.username = ''
            self.password = ''

    def get_user(self, username):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        if self.Config.user['backend'] == 'mysql':
            db.execute(self.queryUnameSelect, (username))
        elif self.Config.user['backend'] == 'simplemachines':
            db.execute(self.querySMFUnameSelect, (username))
        else:
            # TODO: Throw an exception here, but I don't know how to do that
            #       at the moment :(
            pass

        row = db.fetchone()

        try:
            self.id = row[0]
            self.username = row[1]
            self.password = row[2]
        except:
            self.id = 0
            self.username = ''
            self.password = ''

    def passcomp(self, password):
        hashpass = hashlib.sha1(self.username.lower() + password)

        print "<h1> COMPARING: {0} TO: {1}".format(hashpass.hexdigest(), self.password)

        if hashpass.hexdigest() == self.password:
            return True
        
        return False
