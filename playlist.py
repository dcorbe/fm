from DB import *
from config import *
from users import User
from song import Song

class Playlist():
    queryGetPlaylist = """
        SELECT name, description 
        FROM playlist_settings 
        WHERE id = %s
    """
    queryGetSongs = """
        SELECT i_song
        FROM playlists
        WHERE listnum = %s AND i_user = %s
    """
    queryGetSongs = """
        SELECT i_song
        FROM playlists
        WHERE listnum = %s AND i_user = %s
    """
    queryCountSongs = """
        SELECT COUNT(*)
        FROM playlists
        WHERE listnum = %s AND i_user = %s
    """
    
    def __init__(self, i_playlist=0, i_user=0, config=None):
        self.id = 0
        self.name = False
        self.description = False
        self.i_user = 0
        self.owner = User()
        self.songs = []
        self.count = 0;
        
        if config:
            self.Config = config
        else:
            self.Config = Config()

        if i_user:
            self.i_user = i_user

        if i_playlist:
            self.open(i_playlist)

    def open(self, i_playlist, i_user=0, get_songs=False):
        self.id = i_playlist

        if i_user > 0:
            self.i_user = i_user
            
        if self.i_user:
            self.owner.open(self.i_user)

        self.get_song_count()
        
        if get_songs:
            self.get_songs()
        
    def get_playlist_info(self, i_playlist=0):
        try:
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        db.execute(self.queryGetPlaylist, (i_playlist))
        row = db.fetchone()
        
        try:
            self.description = row[1]
            self.name = row[0]
        except:
            self.id = 0
            self.name = False
            self.description = False
            self.i_user = 0
            self.owner.open(0)

    def get_songs(self):
        try:            
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        db.execute(self.queryGetSongs, (self.id, self.i_user))

        rows = db.fetchall()

        for row in rows:
            song = Song(row[0], self.Config)
            self.songs.append(song)
        

    def get_song_count(self):
        try:            
            db = conn.cursor()
        except NameError:
            conn = DB()
            db = conn.cursor()

        db.execute(self.queryCountSongs, (self.id, self.i_user))

        row = db.fetchone()

        self.count = row[0]
