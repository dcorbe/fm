from mutagen.easyid3 import EasyID3
import os, sys, mutagen
import MySQLdb

from DB import *
import tags

conn = DB()

def scan(directory):
    for i in os.listdir(directory):
        if os.path.isdir("{0}/{1}".format(directory, i)):
            if scan("{0}/{1}".format(directory, i)) == 1:
                print '{0}/{1}'.format(directory, i)

        elif i.endswith(".mp3"):
            if loadmp3("{0}/{1}".format(directory, i)) == 0:
                return 0
        elif i.endswith(".MP3"):
            if loadmp3("{0}/{1}".format(directory, i)) == 0:
                return 0
    return 1

def loadmp3(file):
    db = conn.cursor()

    try:
        tag = EasyID3(file)
    except mutagen.id3.ID3NoHeaderError:
        return 0

    try:
        artist = u''.join(tag['artist'])
    except KeyError:
        return 0

    try:
        title = u''.join(tag['title'])
    except KeyError:
        return 0

    db.execute("SELECT * FROM songs WHERE artist = %s AND title = %s", 
               (artist.encode('UTF-8'), title.encode('UTF-8')))
    if db.rowcount > 0:
        return 0
    else:
        return 1

    
# main() in python herp
if __name__ == "__main__":
    try:
        scan(sys.argv[1])
    except IndexError:
        print "Please specify a directory"
        print EasyID3.valid_keys.keys()
