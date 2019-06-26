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
mc = memcache.Client(['memcached:11211'], debug=0)

@app.route('/display', methods=['POST'])
def display():
    return render_template("1vs1.html")

@app.route('/admin-hidden-stuff', methods=['GET', 'POST'])
def admin_stuff():
    if request.method == 'POST':
      if 'json' in request.form:
        data = json.loads(request.form['json'])
        key = data['settings']['cup']
        mc.set("%s_config" % key, request.form['json'])
        d = mc.get('simulation_keys')
        if not d:
          d = []
        if key not in d:
          d.append(key)
          mc.set("simulation_keys", json.dumps(d))
          logging.info("Updated 'simulation_keys' with '%s'" % key)
        logging.info("Updated '%s_config'" % key)
    return render_template("admin.html")

@app.route('/', methods=['GET'])
def default():
    return render_template("index.html")

@app.route('/<key>/<scenario>.html', methods=['GET'])
def scenarios(key, scenario):
    return render_template("scenarios/%s/%s.html" % (key, scenario))


