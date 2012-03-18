from post import *
from DB import *
import time
import random
import string

class Topic():
    """ This is the base class for threads.  Extends the Post class """

    queryTopicSelect = """
        SELECT id
        FROM posts
        WHERE i_thread = %s"""

    queryGetLinkHash = """
        SELECT *
        FROM links
        WHERE i_thread = %s"""

    querySearchByLinkHash = """
        SELECT *
        FROM links
        WHERE linkhash = %s"""

    # TODO: Probably redundant...  
    # couldn't we could do this with p.new() instead?
    queryInsertPost = """
        INSERT INTO posts
        (
            subject, post, ts, i_user, i_thread
        )
        VALUES
        (
            %s, %s, %s, %s, %s
        )"""

    queryInsertLink = """
	UPDATE posts
	SET i_thread = %s
	WHERE id = %s
        """

    queryInsertLinkHash = """
        INSERT INTO links
        (
            i_thread, linkhash
        )
        VALUES
        (
            %s, %s
        )"""

    queryAddSubscription = """
        INSERT INTO subscriptions
        (
            i_thread, i_user
        )
        VALUES
        (
            %s, %s
        )"""

    queryBump = """
	UPDATE threads
	SET bumped = %s
        WHERE id = %s
	"""

    queryNewThread = """
	INSERT INTO threads
	(
	    subject
	)
	VALUES
	(
	    %s
	)"""

    def __init__(self, i_topic=None):
        self.id = None
        self.posts = [ ]
        self.subject = None
        self.ts = 0
        self.bumped = 0
        self.postcount = 0
        self.linkhash = None

        if i_topic:
            self.open(i_topic)

    def open(self, i_topic):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        db.execute(self.queryTopicSelect, (i_topic))
        posts = db.fetchall()
        
        for row in posts:
            self.postcount = self.postcount + 1
            post = Post();
            post.open(row[0])
            self.posts.append(post)

        self.subject = self.posts[0].subject
        self.bumped = post.ts
        self.linkhash = self.getLinkHash(i_topic)
        self.id = i_topic

    def getLinkHash(self, i_topic):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()
        
        db.execute(self.queryGetLinkHash, (i_topic))
        row = db.fetchone();
        return row[2]

    def searchby_linkhash(self, linkhash):
        """ Used to generate a thread ID from the supplied link """
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()
        
        db.execute(self.querySearchByLinkHash, (linkhash))
        row = db.fetchone()
        i_thread = row[1]
        self.open(i_thread)
    
    def insert(self, i_thread, post, i_user, subject=None):
        """ Inserts a new post into the current thread """

        # Hold over from my C days.  tv = struct timeval.  
        # I know! but sorry I don't have better variable name :(
        tv = int(time.time());

        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        if not subject:
            subject = self.subject

        p = Post()

        # Insert post
        db.execute(self.queryInsertPost, (subject, post,
                   tv, i_user, self.id))

        # Update thread bump time
        self.bump(tv)

        # Get last insert ID
        p.id = db.lastrowid

        # Refresh post data
        p.open(p.id)

        # Link post to this thread
        self.posts.append(p)

    def link(self, post):
        """ This is used to link a post to this thread """
    
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        db.execute(self.queryInsertLink, (self.id, post.id))
        
        self.posts.append(post)

    def genhash(self):
        """ This function is used to generate a linkhash for new threads """

        if self.linkhash:
            return

        # Generate the hash
        s = ''
        for x in range(12):
            s = s + s.join(random.choice(string.ascii_uppercase + 
                                         string.ascii_lowercase +
                                         string.digits))

        # Insert it into the DB
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        db.execute(self.queryInsertLinkHash, (self.id, s))

        self.linkhash = s
    
    def subscribe(self, i_user):
        """ Subscribe a user to a thread """

        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()
        
        db.execute(self.queryAddSubscription, (self.id, i_user))

    def bump(self, tv=None):
        """ Update the bump time of the current thread """

        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        # Hold over from my C days.  tv = struct timeval.  
        # I know! but sorry I don't have better variable name :(
        if not tv:
            tv = int(time.time());

        db.execute(self.queryBump, (tv, self.id))

        
    def new(self, subject=None):
        """ Generates a new thread number """

        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        #db.execute("SELECT count(*) FROM threads")
        #row = db.fetchone()
        #count = int(row[0])
        #count = count + 1
        #db.execute("UPDATE stats SET count={0}".format(count))

        db.execute(self.queryNewThread, (subject))
        self.id = db.lastrowid

        self.bump()
