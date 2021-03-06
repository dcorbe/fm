from flask import Flask, session, request, redirect, url_for, render_template
from werkzeug import secure_filename
from werkzeug.contrib.fixers import ProxyFix
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import hashlib
import random
import string

from DB import *
from users import User
from composer import compose
from forum import forum
from blog import blog
from config import *
from playlist import Playlist
import api

app = Flask(__name__)
app.register_blueprint(forum)
app.register_blueprint(blog)
app.register_blueprint(compose)
app.jinja_env.autoescape = False
Config = Config()
conn = DB()

@app.route('/')
def main():
    return render_template('landing.html', api=api)

@app.route('/playlist')
def playlist():
    db = conn.cursor()
    history = [ ]
    requests = [ ]

    db.execute("SELECT * FROM history ORDER BY id")
    rows = db.fetchall()
    for row in rows:
        i_user = row[2]
        history.append(get_song(row[1], i_user=i_user))

    # Get the request list
    db.execute("SELECT * FROM requests ORDER BY id")
    rows = db.fetchall()
    for row in rows:
        i_user = row[2]
        requests.append(get_song(row[0], i_user=i_user))

    # Last song in this history list is what's currently playing
    playing = history.pop()

    return render_template("playlist.html", api=api,
                           history=history, playing=playing, requests=requests)

@app.route('/xml/playlist')
def xmlrpc_playlist():
    db = conn.cursor()
    history = [ ]
    requests = [ ]

    db.execute("SELECT * FROM history ORDER BY id DESC")
    rows = db.fetchall()
    for row in rows:
        i_user = row[2]
        history.append(get_song(row[1], i_user=i_user))

    # Get the request list
    db.execute("SELECT * FROM requests ORDER BY id DESC")
    rows = db.fetchall()
    for row in rows:
        i_user = row[2]
        requests.append(get_song(row[0], i_user=i_user))

    # Last song in this history list is what's currently playing
    playing = history.pop()

    # Create the XML
    root = Element('playlist')
    parent = SubElement(root, "nowplaying")
    child = SubElement(parent, "song")
    attribs = {'artist': playing['artist'],
              'title': playing['title'],
              'requestby': playing['username']}
    child.attrib = attribs

    parent = SubElement(root, "history")
    for song in history:
        child = SubElement(parent, "song")
        attribs = {'artist': song['artist'],
                   'title': song['title'],
                   'requestby': song['username']}
        child.attrib = attribs

    parent = SubElement(root, "upcoming")
    for song in requests:
        child = SubElement(parent, "song")
        attribs = {'artist': song['artist'],
                   'title': song['title'],
                   'requestby': song['username']}
        child.attrib = attribs

    # FIXME: there literally has to be a better way to do this.
    return parseString(tostring(root)).toprettyxml()

@app.route('/search', methods=['GET', 'POST'])
def search():
    db = conn.cursor()
    results = [ ]

    # Contextual searching
    if 'i_playlist' in session and 'i_user' in session:
        playlist = Playlist(session['i_playlist'], session['i_user'])
    else:
        # TODO: Template problem here.  
        session['i_playlist'] = 0
        playlist = Playlist()
        
    if request.method == "POST":
        artist = request.form['artist']
        title = request.form['title']

        # We don't want people to be able to return every song in the database
        if artist == '' and title == '':
            return redirect(url_for('search'))
        
        # Sanity checks
        if artist == '':
            artist = '%'
        if title == '':
            title = '%'

        # TODO: exact matching
        db.execute("SELECT * FROM songs WHERE artist LIKE %s AND title LIKE %s",
                       ('%{0}%'.format(artist), '%{0}%'.format(title)))

        rows = db.fetchall()
        for row in rows:
            results.append({'i_song': row[0],
                         'artist': row[1].decode('UTF-8'),
                         'title': row[2].decode('UTF-8'),
                            'path': row[3]})

        return render_template("searchresults.html", results=results, api=api, playlist=playlist)
    else:
        return render_template("search.html", api=api)

@app.route('/request/<i_song>')
def song_request(i_song=False):
    db = conn.cursor()

    if 'username' in session:
        db.execute("INSERT INTO requests (i_song, i_user) VALUES (%s, %s)", 
                   (i_song, session['i_user']))
        return redirect(url_for('playlist'))
    else:
        return redirect(url_for('login', next=request.url))

# /vote with no params needs to elicit an ajax response
@app.route('/vote', methods=['GET', 'POST'])
@app.route('/vote/<i_song>/<rating>')
def vote_test(i_song=False, rating=False):
    db = conn.cursor()

    if not 'username' in session:
        return redirect(url_for('login', next=request.url))

    if (request.method == "POST"):
        i_user = session['i_user']
        for i_song in request.form:
            rating = int(request.form[i_song])
            cur = get_rating(i_song, i_user)
            if cur > 0:
                db.execute("UPDATE votes SET vote=%s WHERE i_song=%s AND i_user = %s", 
                           (rating, i_song, i_user))
            else:
                db.execute("INSERT INTO votes (i_song, i_user, vote) VALUES (%s, %s, %s)", 
                           (i_song, i_user, rating))

    return 'success'

def get_average(i_song):
    db = conn.cursor()
    count = 0
    votes = 0

    db.execute("SElECT * FROM votes WHERE i_song = %s", (i_song))
    rows = db.fetchall()
    for row in rows:
        count = count + int(row[1])
        votes = votes + 1

    if votes > 0:
        average = (count / votes)
    else:
        average = 0

    return [average, votes]

def get_rating(i_song, i_user):
    db = conn.cursor()

    db.execute("SELECT * FROM votes WHERE i_song = %s AND i_user = %s", 
               (i_song, i_user))

    rows = db.fetchall()

    try:
        vote = int(rows[0][1])
    except:
        vote = 0

    return vote

#
# This is being deprecated in favor of the Song class
#
def get_song(i_song, i_user=False):
    db = conn.cursor()

    db.execute("SELECT * FROM songs WHERE id = %s", (i_song))
    songs = db.fetchall()
    song = songs[0]
    
    try:
        result = {'i_song': song[0],
                  'artist': song[1].decode('UTF-8'),
                  'title': song[2].decode('UTF-8'),
                  'path': song[3]}
    except:
        result = {'i_song': song[0],
                  'artist': song[1],
                  'title': song[2],
                  'path': song[3]}

    # Populate user information
    result['i_user'] = i_user
    result['username'] = get_username(i_user)

    # Populate rating information if available
    if i_user:
        result['rating'] = get_rating(i_song, i_user);

    (result['average'], result['votes']) = get_average(i_song)

    return result

#
# This could be repalced by the equivalent class in the forum code
#
def get_username(i_user):
    user = User(i_user)
    return user.username

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if api.logged_in(session):
        del session['username']
        session['i_user'] = 0

    return redirect(api.redirect_url(request))

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = User();

    if request.method == "POST":
        user.get_user(request.form['username'])

        if user.username == 'Random':
            return "User not in database."

        if user.passcomp(request.form['password']) == True:
            session['username'] = request.form['username']
            session['i_user'] = user.id
            session['i_playlist'] = 0
            print "request.get['next'] = {0}".format(request.args.get('next'))
            return redirect(api.redirect_url(request))
        else:
            return "Login Incorrect"
    else:
        return render_template('login.html', api=api)

@app.route('/sessionset/i_playlist/<i_playlist>')
def session_set_variable_playlist(i_playlist = 0):
    session['i_playlist'] = i_playlist
    return(redirect(api.redirect_url(request)))

@app.route('/user/<i_user>/playlists')
def playlists(i_user = 0):
    if api.logged_in(session):
        print "Returning playlists page"
        return render_template("playlists.html", api=api, session=session, i_user=i_user)
    else:
        return redirect(url_for('login', next=request.url))

@app.route('/user/<i_user>/playlist/<i_playlist>')
def playlist_byuser(i_user = 0, i_playlist = 0):
    p = api.get_playlist(i_user, i_playlist)
    return render_template('editplaylist.html', api=api, session=session, i_user=i_user, i_playlist=i_playlist, playlist=p)

@app.route('/user/<i_user>/playlist/<i_playlist>/song/<i_song>/delete')
def playlist_deletesong(i_user = 0, i_playlist = 0, i_song = 0):
    if api.logged_in(session):
        if int(session['i_user']) == int(i_user):
            api.del_playlist_song(i_user, i_playlist, i_song)
            return redirect(url_for('playlist_byuser', i_user=i_user, i_playlist=i_playlist))
        else:
            # TODO: Error hint here maybe?  
            return "<h1>session['i_user'] = {0}  i_user = {1}</h1>".format(session['i_user'],i_user)
    else:
        return redirect(url_for('login', next=request.url))

@app.route('/user/<i_user>/playlist/<i_playlist>/song/<i_song>/add')
def playlist_addsong(i_user = 0, i_playlist = 0, i_song = 0):
    if api.logged_in(session):
        if int(session['i_user']) == int(i_user):
            api.add_playlist_song(i_user, i_playlist, i_song)
            return redirect(url_for('playlist_byuser', i_user=i_user, i_playlist=i_playlist))            
    else:
        return redirect(url_for('login', next=request.url))

if __name__ == '__main__':
    # If we're running from the command line we want debugging info
    app.debug = True

    # This generates a secure application key which changes every time
    # the app is restarted.
    s = ''
    s = s + s.join(random.choice(string.ascii_uppercase + 
                                         string.ascii_lowercase +
                                         string.digits))
    app.secret_key = hashlib.md5('application' + s).hexdigest()

    # Start the application
    app.run(host='0.0.0.0', port=9002, debug=True, threaded=True)
else:
    # This generates a secure application key which changes every time
    # the app is restarted.
    s = ''
    s = s + s.join(random.choice(string.ascii_uppercase + 
                                         string.ascii_lowercase +
                                         string.digits))
    app.secret_key = hashlib.md5('application' + s).hexdigest()
    app.wsgi_app = ProxyFix(app.wsgi_app)

