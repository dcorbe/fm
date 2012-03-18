from flask import Flask, session, request, redirect, url_for, render_template
from werkzeug import secure_filename
from werkzeug.contrib.fixers import ProxyFix
from DB import *
from bbcode import *
from topics import *
from post import *
from settings import *
from forums import *
from subscriptions import *
import time

app = Flask(__name__)
app.jinja_env.autoescape = False
conn = DB()
bbcode = postmarkup_wrapper()
settings = Settings()

@app.route('/')
def board_main():
    if 'username' in session:
        dict = settings.general()
        if dict['render_forums'] > 0:
            return render_template('index.html')
        else:
            return redirect(url_for('topics'))
    else:
        return redirect(url_for('login'))

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
            return redirect(url_for('topics'))
        else:
            return "Login Incorrect"

    else:
        return render_template('login.html')

@app.route('/topics', methods=['GET', 'POST'])
def topics():
    if not 'username' in session:
        return redirect(url_for('login'))

    s = Subscription(session['i_user'])
    
    return render_template('topics.html', subscriptions=s)

@app.route('/thread/<i_thread>', methods=['GET', 'POST'])
def threadview(i_thread):
    if not 'username' in session:
        return redirect(url_for('login'))

    # Set up the thread container
    if request.method == "POST":
        t = Topic(i_thread)
    else:
        t = Topic()

        t.searchby_linkhash(i_thread)

        return render_template('thread.html', thread=t, bbcode=bbcode, time=time)

    # Process a quick reply for this thread
    t.insert(i_thread, request.form['postbody'], session['i_user'])

    return render_template('thread.html', thread=t, bbcode=bbcode, time=time)

@app.route('/thread/new', methods=['GET', 'POST'])
def newthread():
    if not 'username' in session:
        return redirect(url_for('login'))
    
    u = User(session['i_user'])

    if request.method == "POST":
        t = Topic()
        p = Post()
        u = User(session['i_user'])


        # Insert thread first.
        t.new(request.form['subject'])

        # Insert post next.
        p.subject = request.form['subject']
        p.post = request.form['postbody']
        p.i_user = u
        p.new()

        # Link post to thread
        t.link(p)

        # Generate a link hash for this thread.
        t.genhash()

        # Finally subscribe the user to the thread.
        t.subscribe(u.id)

        # Redirect the user to the new thread.
        return redirect('/thread/{0}'.format(t.linkhash))

    else:
        return render_template('newthread.html', user=u)

if __name__ == '__main__':
    app.debug = True
    app.secret_key = '2b6a57457a69559a69678bca4d5ab023'
    app.run(host='127.0.0.1', port=9001)
else:
    app.secret_key = '2b6a57457a69559a69678bca4d5ab023'
    app.wsgi_app = ProxyFix(app.wsgi_app)
