from DB import *
#from users import *
from simplemachines import *
import time

class Post():
    """ This is a base class for "posts" 
    an i_thread of 0 has special meaning:  It's a blog post"""

    queryPostSelect = """
        SELECT *
        FROM posts
        WHERE id = %s"""

    queryAddPost = """
        INSERT INTO posts
            (subject, post, ts, i_user)
        VALUES
            (%s, %s, %s, %s)"""

    queryByThread = """
        SELECT *
        FROM posts
        WHERE i_thred = %s"""

    def __init__(self, i_post=None):
        self.id = 0;
        self.subject = None;
        self.post = None;
        self.ts = 0;
        self.i_user = None;

        if i_post:
            self.open(i_post)

    def open(self, i_post):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        db.execute(self.queryPostSelect, (i_post))
        post = db.fetchone()

        self.id = post[0]
        self.subject = post[1]
        self.post = post[2]
        self.ts = post[3]
        self.i_user = User(post[4])

    def new(self):
        """ This is used to insert a new post into the database """
        
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()
        

        db.execute(self.queryAddPost, (self.subject, self.post,
                                          int(time.time()),
                                          self.i_user.id))

        self.id = db.lastrowid


