from flask import Blueprint, render_template, redirect
from jinja2 import TemplateNotFound
from utils import get_uid, get_session, render_with_appname


main = Blueprint('main', __name__, template_folder='templates', static_folder='static')

@main.route('/')
def home_path():  # put application's code here
    if get_uid() == '':
        return redirect('/login')

    ctx = {
        'title': 'Home',
        'content': 'Welcome to the home page',
        'session': get_session(),
        'uid': get_uid()
    }
    return render_with_appname('home.html', context=ctx )

