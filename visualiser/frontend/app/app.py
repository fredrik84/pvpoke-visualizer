#!/usr/bin/python3
import json
import os
import re
from flask import Flask
from flask import render_template
from flask import request
from flask import abort
from flask import flash
import logging
import traceback
import time
import memcache
import pprint
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)-8s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
stats = json.load(open("stats.txt"))
mc = memcache.Client(['memcached-visualiser:11211'], debug=0)

@app.route('/display', methods=['POST'])
def display():
    return render_template("1vs1.html")

@app.before_request
def before_request():
    if request.method == 'POST':
        pprint.pprint(request.form['json'])        

@app.route('/')
def default():
    return render_template("index.html")

