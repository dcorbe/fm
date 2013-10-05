from DB import *
from post import *
from user import *
from topics import *

def logged_in():
    if 'username' in session:
        return True
    else:
        return False

#
# TODO: NEEDS PAGINATION
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
