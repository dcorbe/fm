from flask import Blueprint, session, request, redirect, url_for, render_template
from werkzeug import secure_filename
from werkzeug.contrib.fixers import ProxyFix
from DB import *
from bbcode import *
from topics import *
from post import *
from settings import *
from forums import *
from subscriptions import *
import api
import time

forum = Blueprint('forum', __name__)

conn = DB()
bbcode = postmarkup_wrapper()
settings = Settings()

@forum.route('/forum')
def board_main():
    if 'username' in session:
        dict = settings.general()
        if dict['render_forums'] > 0:
            return render_template('forum.html', api=api)
        else:
            return redirect(url_for('forum.topics'))
    else:
        return redirect(api.redirect_url(request))

@forum.route('/topics', methods=['GET', 'POST'])
def topics():
    if not 'username' in session:
        return redirect(url_for('login'))

    s = Subscription(session['i_user'])
    
    return render_template('topics.html', subscriptions=s, api=api)

@forum.route('/thread/<i_thread>', methods=['GET', 'POST'])
def threadview(i_thread):
    if not 'username' in session:
        return redirect(url_for('login'))

    # Set up the thread container
    if request.method == "POST":
        t = Topic(i_thread)
    else:
        t = Topic()

        t.searchby_linkhash(i_thread)

        return render_template('thread.html', thread=t, bbcode=bbcode, time=time, api=api)

    # Process a quick reply for this thread
    t.insert(i_thread, request.form['postbody'], session['i_user'])

    return render_template('thread.html', thread=t, bbcode=bbcode, time=time, api=api)

@forum.route('/thread/new', methods=['GET', 'POST'])
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
        return render_template('newthread.html', user=u, api=api)

