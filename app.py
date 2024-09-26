from uuid import uuid4
import requests
from flask import Flask, render_template, session, redirect, request
from flask_session import Session
from dotenv import load_dotenv
import os
from utils import get_uid, get_session, render_with_appname
from main import main
from meters import meters_bp

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.register_blueprint(main)
app.register_blueprint(meters_bp, url_prefix='/meters')


app.config['SESSION_TYPE'] = os.getenv('SESSION_TYPE', 'filesystem')
app.config['SESSION_FILE_DIR'] = os.getenv('SESSION_FILE_DIR', 'c:\\temp')
app.config['SESSION_PERMANENT'] = os.getenv('SESSION_PERMANENT', False)
app.config['SESSION_USE_SIGNER'] = os.getenv('SESSION_USE_SIGNER', True)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecret')


Session(app)


@app.route('/login', methods=['GET', 'POST'])
def login():

    def create_url(part1,part2) -> str:
        if part1.endswith('/'):
            part1 = part1[:-1]
        if part2.startswith('/'):
            part2 = part2[1:]
        return f'{part1}/{part2}'


    # handle if post
    if request.method == 'POST':
        # get the username and password
        username = request.form.get('username')
        password = request.form.get('password')
        # check if the username and password are correct
        auth_api = os.getenv('AUTH_API', '')
        auth_group = os.getenv('AUTH_GROUP', '')
        if auth_api == '':
            # call the auth api
            pass
        # check if the username and password are correct
        form_body = {
            'username': username,
            'password': password
        }
        api_result = requests.post(create_url(auth_api, auth_group), json=form_body)
        if api_result.status_code == 401:
            # if the username and password are incorrect
            session['uid'] = ''
            session['loginSuccess'] = ''
            session['message'] = f'Error logging in as {username}'
            return redirect('/login')

        if api_result.status_code == 206:
            # convert api_result.txt to an object
            msg = api_result.json()['message']
            # if response text is 'success' then the username and password are correct
            # if the username and password are incorrect
            session['uid'] = ''
            session['loginSuccess'] = ''
            session['message'] = f'Error logging in as {username}: not member of {auth_group}'
            return redirect('/login')
        if api_result.status_code == 200:
            # set the session uid to the username
            session['uid'] = username
            session['loginSuccess'] = 'success'
            session['message'] = ''
            return redirect('/')
        else:
            # something was incorrect, so redirect to the login page
            msg = api_result.json()['message']
            session['message'] = f'Error logging in as {username}: {msg}'
            return redirect('/login')
    else:
        # handle get request
        ctx = {
            'title': 'Login',
            'content': 'Welcome to the login page',
            'session': get_session(),
            'uid': get_uid(),
            'message': session.get('message', '')
        }
        return render_with_appname('login.html', context=ctx)

@app.route('/logout')
def logout():
    session.pop('uid', None)
    session.pop('loginSuccess', None)
    ctx = {
        'title': 'Login',
        'content': 'Welcome to the login page',
        'session': get_session(),
        'uid': get_uid()
    }
    return render_with_appname('home.html', context=ctx)


if __name__ == '__main__':
    app.run()
