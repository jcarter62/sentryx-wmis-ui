from flask import Blueprint, render_template, redirect, request
#from jinja2 import TemplateNotFound
from utils import get_uid, get_session, render_with_appname
import requests
import os


meters_bp = Blueprint('meters_bp', __name__, template_folder='templates', static_folder='static', url_prefix='/meters')

def extract_number(s) -> int:
    if s is None:
        instr = '0'
    else:
        instr = s

    rslt = 0
    try:
        n = ''
        for c in s:
            if c.isdigit():
                n += c
        rslt = int(n)
    except:
        rslt = 0
    return rslt

@meters_bp.route('/', methods=['GET', 'POST'])
def list_meters():
    targetdate = None
    if get_uid() == '':
        return redirect('/login')

    if request.method == 'POST':
        # get targetdate
        targetdate = request.form.get('targetdate')


    # load DATA_API + /api/meter-list and display the list of meters
    data = []
    items = []
    data_ok = False
    url = os.getenv('DATA_API', '') + '/api/sp_ami_readings'
    if not(targetdate is None):
        url += f'/{targetdate}'

    api_result = requests.get(url)
    if api_result.status_code == 200:
        data = api_result.json()
        data_ok = True
    else:
        data = [{'error': 'Error loading'}]
        data_ok = False

    if data_ok:
        items = data[0]['data']
        for item in items:
            item['reading'] = round(item['reading'], 4)
            item['lastreading'] = round(item['lastreading'], 4)
        items.sort(key=lambda x: x['meter_id'])

    ctx = {
        'title': 'Meters',
        'content': 'List of meters',
        'session': get_session(),
        'uid': get_uid(),
        'data': items,
        'targetdate': targetdate,
    }
    return render_with_appname('meters.html', context=ctx )

@meters_bp.route('/last-wmis-reading/<meter_id>', methods=['POST'])
def lwr(meter_id:str):
    data = []
    url = os.getenv('DATA_API', '') + '/api/last-wmis-reading/' + meter_id

    api_result = requests.get(url)
    code = api_result.status_code
    if code == 200:
        data = api_result.json()
    else:
        data = [{'error': 'Error loading'}]

    return data[0]['data'],code

@meters_bp.route('/post-reading/<meter_id>/<reading_date>/<reading>/<uid>', methods=['POST'])
def post_reading(meter_id:str, reading_date:str, reading:str, uid:str):
    data = []
    apicode = 500
    url = os.getenv('DATA_API', '') + f'/api/post-reading/{meter_id}/{reading_date}/{reading}/{uid}'

    api_result = requests.post(url)
    code = api_result.status_code
    if code == 200:
        data = api_result.json()
        apicode = data[1]
    elif code == 208:
        data = api_result.json()
        apicode = data[1]
    else:
        data = [{'error': 'Error loading'}]
        apicode = 500

    return data[0],apicode

@meters_bp.route('/process-readings', methods=['POST'])
def process_readings():
    data = []
    url = os.getenv('DATA_API', '') + '/api/process-readings'

    api_result = requests.post(url)
    code = api_result.status_code
    if code == 200:
        data = api_result.json()
    else:
        data = [{'error': 'Error loading'}]

    return data[0],code
