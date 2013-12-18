import time

from DB import *
from post import *
from user import *
from topics import *
from forums import *

def logged_in(session):
    if 'username' in session:
        return True
    else:
        return False

#
# TODO: NEEDS PAGINATION
# FIXME: really?  We're running DB queries here?
#
def posts_bythread(i_thread):
    result = { }
    posts = [ ]

    try:
        db = conn.cursor()
    except NameError:
        conn = DB()
        db = conn.cursor()
        
    db.execute("""SELECT id
                  FROM posts 
                  WHERE i_thread = %s
                  ORDER BY ts DESC""", (i_thread))

    rows = db.fetchall()
    for row in rows:
        result = Post(row[0])
        # result['user'] = User(row[1])
        # result['thread'] = Topic(row[2])
        posts.append(result)

    return posts

#
# FIXME really?  We're running DB queries here?
#
def blog_posts():
    result = { }
    posts = [ ]

    try:
        db = conn.cursor()
    except NameError:
        conn = DB()
        db = conn.cursor()

    db.execute("""SELECT id
                  FROM posts
                  WHERE blog = 'Y'""")

    rows = db.fetchall()

    for row in rows:
        result = Post(row[0])
        posts.append(result)

    return posts

#
# TODO consult the settings file for the default redirect information
#      in any case we should make a better effort to ask the user what
#      they would like to do on redirects.
def redirect_url(request, default='playlist'):
    return request.args.get('next') or \
           request.referrer or \
           '/blog'

#
# This returns the list of categories to the template system
#
def categories():
    f = Forum()
    return f.categories()

#
# Return a list of forums by category
#
def forums(i_category=0):
    f = Forum()
    return f.forums(i_category)

#
# This converts a unix timestamp to a readable date.
# The fmt argument takes its values from time.strftime().  See:
# http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
#
def unixts(ts=0, fmt=None):
    if not fmt:
        config = Config()
        fmt = config.forum['fmt']

    return time.strftime(fmt, time.localtime(ts));
