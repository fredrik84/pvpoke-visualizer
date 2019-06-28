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
from prometheus_flask_exporter import PrometheusMetrics

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)-8s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
metrics = PrometheusMetrics(app)
mc = memcache.Client([os.environ.get('MEMCACHED', 'memcached')], debug=0)

@app.route('/display', methods=['POST'])
def display():
    return render_template("1vs1.html")

@app.route('/admin-hidden-stuff', methods=['GET', 'POST'])
@metrics.do_not_track()
def admin_stuff():
    if request.method == 'POST':
      if 'json' in request.form:
        data = json.loads(request.form['json'])
        key = "-".join((data['settings']['cup'], str(data['settings']['my_shield']), str(data['settings']['op_shield'])))
        mc.set("%s_config" % key, request.form['json'])
        d = mc.get('simulation_keys')
        if not d:
          d = []
        else:
          d = json.loads(d)
        if key not in d:
          d.append(key)
          mc.set("simulation_keys", json.dumps(d))
          logging.info("Updated 'simulation_keys' with '%s'" % key)
        logging.info("Updated '%s_config'" % key)
    return render_template("admin.html")

@app.route('/<key>/<scenario>.html', methods=['GET'])
def scenarios(key, scenario):
    return render_template("scenarios.html", data=(key, scenario))

@app.route('/', methods=['GET'])
def default():
    k = sorted(json.loads(mc.get('simulation_keys')))
    keys = {}
    for key in k:
      tmp = key.split("-")
      if len(tmp) >= 2:
        if tmp[0] not in keys:
          keys[tmp[0]] = []
        keys[tmp[0]].append({'mshield': tmp[1], 'oshield': tmp[2]})
    return render_template("index.html", data=keys)
