from flask import Blueprint, session, request, redirect, url_for, render_template
from werkzeug import secure_filename
from werkzeug.contrib.fixers import ProxyFix
from DB import *
from bbcode import *
from users import *
from topics import *
from forums import *
from post import *
import api

compose = Blueprint('compose', __name__)

conn = DB()

@compose.route('/compose', methods=['GET', 'POST'])
def composer():
    if api.logged_in(session):
        pass
    else:
        return("<h1>Error: you must be signed in to do that</h1>")

    # The options dict is always passed to the composed
    # The general options are explained below.
    options = dict()

    # The original (or quoted) text, if any.
    options['text'] = None

    # Lock the composer to a specific thread (post a comment or reply)
    options['thread'] = Topic()

    # Lock the composer to a specific forum (typically a new thread)
    options['forum'] = Forum()

    if request.method == "POST":
        if 'text' in request.form:
            options['text'] = request.form['text']
        if 'thread' in request.form:
            options['thread'].open(int(request.form['thread']))
        if 'forum' in request.form:
            options['forum'].open(int(request.form['forum']))

    return render_template('composer.html', api=api, options=options)

@compose.route('/compose/new', methods=['POST'])
def post():
    if api.logged_in(session):
        pass
    else:
        return("<h1>Error: you must be signed in to do that</h1>")

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
