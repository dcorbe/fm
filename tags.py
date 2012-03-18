from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.oggvorbis import OggVorbis
import os, sys, mutagen
import MySQLdb

from DB import *

conn = DB()

def scan(directory):
    for i in os.listdir(directory):
        if os.path.isdir("{0}/{1}".format(directory, i)):
            scan("{0}/{1}".format(directory, i))
        elif i.endswith(".mp3"):
            loadmp3("{0}/{1}".format(directory, i)) 
        elif i.endswith(".MP3"):
            loadmp3("{0}/{1}".format(directory, i)) 
        elif i.endswith(".FLAC"):
            loadflac("{0}/{1}".format(directory, i)) 
        elif i.endswith(".flac"):
            loadflac("{0}/{1}".format(directory, i)) 
        elif i.endswith(".ogg"):
            print "OOG: {0}".format(i)

def loadflac(file):
    db = conn.cursor()
    
    # Check to see if the file aready exists in the DB before we proceed
    db.execute("SELECT * FROM songs WHERE path = %s", (file))
    if db.rowcount > 0:
        print "SKIPPING: {0}".format(file)
        return 0

    # Scan for a tag
    try:
        tag = FLAC(file)
    except:
        print "UNTAGGED (Adding Anyways) {0}".format(file)
        try:
            db.execute("INSERT INTO songs (path) VALUES (%s)", (file))
        except:
            print "SKIPPING: {0}".format(file)
        return

    # Try and read the tag
    try:
        artist = u''.join(tag['artist'])
    except KeyError:
        artist = u'Unknown'

    try:
        title = u''.join(tag['title'])
    except KeyError:
        title = u'Unknown'

    # INserts into databases
    print "ADDING: {0} - {1}".format(artist.encode('UTF-8'), title.encode('UTF-8'))

    try:
        db.execute("INSERT INTO songs (artist, title, path) VALUES (%s, %s, %s)", (artist.encode('UTF-8'), title.encode('UTF-8'), file))
    except:
        print "SKIPPING: {0}".format(file)


def loadmp3(file):
    db = conn.cursor()

    # Check to see if the file aready exists in the DB before we proceed
    db.execute("SELECT * FROM songs WHERE path = %s", (file))
    if db.rowcount > 0:
        print "SKIPPING: {0}".format(file)
        return 0

    try:
        tag = EasyID3(file)
    except mutagen.id3.ID3NoHeaderError:
        print "UNTAGGED (Adding Anyways) {0}".format(file)
        try:
            db.execute("INSERT INTO songs (path) VALUES (%s)", (file))
        except:
            print "SKIPPING: {0}".format(file)
        return

    try:
        artist = u''.join(tag['artist'])
    except KeyError:
        artist = u'Unknown'

    try:
        title = u''.join(tag['title'])
    except KeyError:
        title = u'Unknown'

    print "ADDING: {0} - {1}".format(artist.encode('UTF-8'), title.encode('UTF-8'))

    try:
        db.execute("INSERT INTO songs (artist, title, path) VALUES (%s, %s, %s)", (artist.encode('UTF-8'), title.encode('UTF-8'), file))
    except:
        print "SKIPPING: {0}".format(file)


# main() in python herp
if __name__ == "__main__":
    try:
        scan(sys.argv[1])
    except IndexError:
        print "Please specify a directory"
        print EasyID3.valid_keys.keys()
