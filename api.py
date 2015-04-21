import time

from DB import *
from post import *
from user import *
from topics import *
from forums import *
from playlist import *
from flask import url_for

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

#
# This should be run from a python shell periodically to reindex
# post count statistics. 
#
def reindex():
    f = Forum()

    threads = 0;
    posts = 0;
    categories = f.categories()
    for category in categories:
        forums = f.forums(category['id'])
        
        for forum in forums:
            f.open(forum['id'])
            threads = threads + f.threadcount
            
            for thread in f.threads:
                posts = posts + thread.postcount
                thread.updatecount(thread.postcount)

    print "Indexed {0} posts in {1} threads".format(posts, threads)


#
# Get a list of playlists maintained by a given user
#
def get_playlists(i_user=0):
    playlists = [ ]
    listenum = { }

    try:
        db = conn.cursor()
    except NameError:
        conn = DB()
        db = conn.cursor()
        
    db.execute("""SELECT id,listnum
                  FROM playlists
                  WHERE i_user = %s
                  ORDER BY listnum,id """, (i_user))

    rows = db.fetchall()

    for row in rows:
        try:
            if listenum[row[1]]:
                continue
        except:
            pass

        listenum[row[1]] = True;
        p = Playlist(row[1], i_user)
        playlists.append(p)

    return playlists

#
# Return a specific playlist
#
def get_playlist(i_user=0, i_playlist=0):
    p = Playlist(i_playlist, i_user)
    p.get_songs()
    return p

#
# Delete a playlist entry
#
def del_playlist_song(i_user=0, i_playlist=0, i_song=0):
    try:
        db = conn.cursor()
    except NameError:
        conn = DB()
        db = conn.cursor()

    db.execute("DELETE FROM playlists WHERE i_user=%s AND listnum=%s AND i_song=%s", (i_user, i_playlist, i_song))


#
# Add a playlist entry
#
def add_playlist_song(i_user=0, i_playlist=0, i_song=0):
    try:
        db = conn.cursor()
    except NameError:
        conn = DB()
        db = conn.cursor()

    print "i_user: {0}".format(i_user)
    print "i_playlist: {0}".format(i_playlist)
    print "i_song: {0}".format(i_song)
    
    db.execute("INSERT INTO playlists (i_user, listnum, i_song) VALUES (%s, %s, %s)", (i_user, i_playlist, i_song))

#
# Get a link to set a session variable
#
def session_setvar_playlist(value = False, redirect_url = False):
    return "{0}?next={1}".format(url_for('session_set_variable_playlist', i_playlist=value), redirect_url)
