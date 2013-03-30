from string import *
import sys
import MySQLdb
import random

# Custom classes
from DB import *

# Set up the app
conn = DB()
songnumber = 0
playlist = [ ]
count = 0

# Function called to initialize your python environment.
# Should return 1 if ok, and 0 if something went wrong.
def ices_init ():
    global conn
    global paylist
    global count

    db = conn.cursor()

    print 'Executing initialize() function..'
    print 'Loading Playlist from DB...'

    db.execute("SELECT * FROM songs")
    songs = db.fetchall()
    for row in songs:
        playlist.append({'i_song': row[0],
                         'artist': row[1],
                         'title': row[2],
                         'path': row[3]})
        count = count + 1

    # Shuffle list
    random.shuffle(playlist)

    return 1

def rpcstart():
    #rpcserver.debug = True
    rpcserver.secret_key = '2b6a57457a69559a69678bca4d5ab023'
    rpcserver.run(host='0.0.0.0', port=12345)

# Function called to shutdown your python enviroment.
# Return 1 if ok, 0 if something went wrong.
def ices_shutdown ():
	print 'Executing shutdown() function...'
	return 1

# Function called to get the next filename to stream. 
# Should return a string.
def ices_get_next ():
    global playlist
    global count
    global songnumber
    global conn

    # Check to see if anything is in the request queue
    db = conn.cursor()

    db.execute("SELECT i_song,id,i_user FROM requests ORDER BY id")

    if db.rowcount > 0:
        rows = db.fetchall()
        i_song = rows[0][0]
        i_request = rows[0][1]
        i_user = rows[0][2]
        db.execute("DELETE FROM requests WHERE id = %s", (i_request))
        db.execute("SELECT * FROM songs WHERE id = %s", (i_song))
        rows = db.fetchall()
        for row in rows:
            add_to_history(i_song, i_user)
            return row[3]

    # Nothing in the playlist so process the shuffle queue
    print 'Executing get_next() function...'

    if (count -1) == songnumber:
        songnumber = 0
    else:
        songnumber = songnumber + 1

    song = playlist[songnumber]

    add_to_history(song['i_song'])
    return song['path']

# This is the function that manages the playlist history
def add_to_history(i_song, i_user=0):
    db = conn.cursor()

    db.execute("INSERT INTO history (i_song, i_user) VALUES (%s, %s)", 
               (i_song, i_user))

    # Trim the oldest part of the history database
    db.execute("SELECT * FROM history ORDER BY id")

    if db.rowcount > 15:
        rows = db.fetchall()
        row = rows[0]
        db.execute("DELETE FROM history WHERE id = %s", (row[0]))

# This function, if defined, returns the string you'd like used
# as metadata (ie for title streaming) for the current song. You may
# return null to indicate that the file comment should be used.
def ices_get_metadata ():
    db = conn.cursor()
    history = [ ]

    db.execute("SELECT * FROM history ORDER BY id")
    rows = db.fetchall()
    for row in rows:
        history.append(get_song(row[1]))

    song = history.pop()
    return '({0}) {1} - {2}'.format(song['i_song'], song['artist'], song['title'])

# Function used to put the current line number of
# the playlist in the cue file. If you don't care about this number
# don't use it.
def ices_get_lineno ():
    global songnumber
    songnumber = songnumber + 1
    return songnumber

def get_song(i_song):
    db = conn.cursor()

    db.execute("SELECT * FROM songs WHERE id = %s", (i_song))
    songs = db.fetchall()
    song = songs[0]
    return({'i_song': song[0],
            'artist': song[1].decode('UTF-8'),
            'title': song[2].decode('UTF-8'),
            'path': song[3]})
