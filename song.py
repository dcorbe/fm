from DB import *
from config import *

class Song():
    querySongSelect = """
        SELECT id, artist, title, path
        FROM songs
        WHERE id = %s"""

    def __init__(self, i_song=0, config=None):
        self.id = 0
        self.artist = False;
        self.title = False;
        self.path = False;

        if config:
            self.Config = config
        else:
            self.Config = Config()

        if i_song:
            self.open(i_song)

    def open(self, i_song): 
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        db.execute(self.querySongSelect, (i_song))

        row = db.fetchone()

        try:
            self.id = i_song
            self.artist = row[1]
            self.title = row[2]
            self.path = row[3]
        except:
            self.id = 0
            self.artist = False
            self.title = False
            self.path = False

        try:
            self.artist = self.artist.decode('UTF-8')
            self.title = self.title.decode('UTF-8')
        except:
            pass
