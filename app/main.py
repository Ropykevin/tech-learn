from flask import Flask,render_template,redirect,url_for,request, jsonify,json,session
from config.Config import *
import datetime, os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

base_url_journeys = 'http://167.71.54.75:8084/'
base_url_company_user = 'http://167.71.54.75:8082/'
base_url_userprogress = 'http://167.71.54.75:8081/'

headers={'Content-type':'application/json', 'Accept':'application/json'}

from utils.filters import *

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=1000)

from views.views import *


if __name__ == '__main__':
    app.run(debug=True)