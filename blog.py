from flask import Blueprint, session, request, redirect, url_for, render_template
from werkzeug import secure_filename
from werkzeug.contrib.fixers import ProxyFix

import time
import api

from DB import *
from bbcode import *
from topics import *
from post import *
from subscriptions import *
import api

blog = Blueprint('blog', __name__)

conn = DB()
bbcode = postmarkup_wrapper()

@blog.route('/blog')
def blog_main():
    posts = api.posts_bythread(0)
    return render_template('blog.html', posts=posts, time=time, api=api,
                           bbcode=bbcode)

