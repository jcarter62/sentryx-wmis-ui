from flask import session, render_template
from flask_session import Session
from uuid import uuid4
import os

def get_session() -> str:
    session_key = session.get('key', None)
    if session_key is None:
        session['key'] = uuid4().hex
        session_key = session['key']
    return session_key

def wipe_session():
    session.pop('key', None)
    return 'Session wiped'

def get_uid()->str:
    try:
        uid = session['uid']
    except:
        uid = ''
    return uid

def render_with_appname(template_name, context):
    context['appname'] = os.getenv('APPNAME', 'flaskapp')
    return render_template(template_name, context=context)

