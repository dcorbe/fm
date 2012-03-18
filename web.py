from flask import Flask, session, request, redirect, url_for, render_template
from werkzeug import secure_filename
from werkzeug.contrib.fixers import ProxyFix

from DB import *

app = Flask(__name__)
app.jinja_env.autoescape = False
conn = DB()

@app.route('/')
def main():
    return render_template('landing.html')

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

    return render_template("playlist.html", 
                           history=history, playing=playing, requests=requests)

@app.route('/search', methods=['GET', 'POST'])
def search():
    db = conn.cursor()
    results = [ ]

    if request.method == "POST":
        artist = request.form['artist']
        title = request.form['title']

        # Sanity checks
        if artist == '':
            artist = '%'
        if title == '':
            title = '%'

        # Execute the search
        db.execute("SELECT * FROM songs WHERE artist LIKE %s AND title LIKE %s",
                   (artist, title))
        rows = db.fetchall()
        for row in rows:
            results.append({'i_song': row[0],
                         'artist': row[1].decode('UTF-8'),
                         'title': row[2].decode('UTF-8'),
                         'path': row[3]})

        return render_template("searchresults.html", results=results)
    else:
        return render_template("search.html")

@app.route('/request/<i_song>')
def song_request(i_song=False):
    db = conn.cursor()

    if 'username' in session:
        db.execute("INSERT INTO requests (i_song, i_user) VALUES (%s, %s)", 
                   (i_song, session['i_user']))
        return redirect(url_for('playlist'))
    else:
        return redirect(url_for('login'))

def get_song(i_song, i_user=False):
    db = conn.cursor()

    db.execute("SELECT * FROM songs WHERE id = %s", (i_song))
    songs = db.fetchall()
    song = songs[0]
    
    result = {'i_song': song[0],
            'artist': song[1].decode('UTF-8'),
            'title': song[2].decode('UTF-8'),
            'path': song[3]}

    if i_user:
        result['i_user'] = i_user
        result['username'] = get_username(i_user)

    return result

def get_username(i_user):
    db = conn.cursor()

    db.execute("SELECT * FROM users WHERE id = %s", (i_user))
    users = db.fetchall()
    user = users[0]

    return user[1]

@app.route('/login', methods=['GET', 'POST'])
def login():
    db = conn.cursor()

    if request.method == "POST":
        db.execute("SELECT * FROM users WHERE username = '{0}'"
                   .format(request.form['username']))
        row = db.fetchone()

        try:
            storedpass = row[2]
        except TypeError:
            return "User not in database."

        if storedpass == request.form['password']:
            session['username'] = request.form['username']
            session['i_user'] = row[0]
            return redirect(url_for('request'))
        else:
            return "Login Incorrect"

    else:
        return render_template('login.html')


def count_requests():
    db = conn.cursor()

    db.execute("SELECT * FROM requests")
    return(db.rowcount)

if __name__ == '__main__':
    app.debug = True
    app.secret_key = '2b6a57457a69559a69678bca4d5ab023'
    app.run(host='0.0.0.0', port=9001)
else:
    app.secret_key = '2b6a57457a69559a69678bca4d5ab023'
    app.wsgi_app = ProxyFix(app.wsgi_app)

