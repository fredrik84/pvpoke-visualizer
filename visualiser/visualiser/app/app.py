#!/usr/bin/python3
from pyvis.network import Network
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import pprint
import os
import re
from flask import Flask
from flask import render_template
from flask import request
from flask import abort
from backports import csv
import hashlib
import logging
import traceback
import time
import memcache
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)-8s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
stats = json.load(open("stats.txt"))
mc = memcache.Client(['memcached-visualiser:11211'], debug=0)

class simulations():
  def __init__(self, entry):
    self.gamemaster = json.load(open('gamemaster.json'))
    # Write stuff to handle the "not combined" json format (missing matk,mdef,opponent and so on)
    self.cup = entry['settings']['cup']
    self.opponent = {
            'shields': entry['settings']['opponent']['shield'],
            'bait': entry['settings']['opponent']['bait']
            }
    try:
        self.matk = entry['settings']['matk']
        self.mdef = entry['settings']['mdef']
    except Exception as e:
        traceback.print_exc()
        logging.info(e)
    self.node_data = []
    self.edge_data = []
    for e in entry['data']:
        self.url = self._generate_url(e)
        d = mc.get(self.url)
        logging.info(self.url)
        if not d:
            logging.info("Data not found in cache, download")
            self.fetch_url(self.url, e['pokemon'])
            self._read_data(e['pokemon'])
        else:
            logging.info("Data found in memcached for %s" % self.url)
            d = json.loads(d)
            self.edge_data = d['edge']
            self.node_data = d['node']

  def _read_data(self, pokemon):
    pokemon = pokemon.replace("(", "").replace(")", "").replace(" ", "_").replace("'", "").lower().title()
    with open('/data/%s_%s.csv' % (pokemon.lower(), self.cup.lower()), encoding='ASCII') as f:
      logging.info("Running simulation for %s" % pokemon)
      result = [row for row in csv.reader(f, delimiter=',')]
      result.pop(0)
      sorted_result = sorted(result, key=lambda x: x[1])[::-1]
      challenger = pokemon.lower().title()
      self.node_data.append({"challenger": challenger, 'challenger_id': stats[challenger]})
      hasher = hashlib.md5()
      hasher.update(challenger.encode('utf-8'))
      color = "#" + hasher.hexdigest()[:6]
      for entry in sorted_result:
        opponent = entry[0].lower().title().replace("(", "").replace(")", "").replace(" ", "_").replace("'", "").lower().title()
        if opponent not in stats:
            logging.info("%s was not found in stats table" % opponent)
            continue
        self.edge_data.append({
          'challenger': challenger,
          'challenger_id': stats[challenger],
          'opponent': opponent,
          'opponent_id': stats[opponent],
          'weight': int(entry[1])/2500,
          'color': color})
    mc.set(self.url, json.dumps({'edge': self.edge_data, 'node': self.node_data}))
    return True

  def _get_moves(self, pokemon,fast,charged1,charged2=None):
    fast = fast.upper().replace(" ", "_")
    charged1 = charged1.upper().replace(" ", "_")
    if charged2:
        charged2 = charged2.upper().replace(" ", "_")

    movelist = []
    for entry in self.gamemaster['pokemon']:
      if entry['speciesId'].lower() == pokemon.lower():
        movelist.append(str(entry['fastMoves'].index(fast)+1))
        movelist.append(str(entry['chargedMoves'].index(charged1)+1))
        if charged2:
          movelist.append(str(entry['chargedMoves'].index(charged2)+1))
        else:
          movelist.append(str(0))
        break
    return movelist

  def _generate_url(self, d):
    moves = self._get_moves(d['pokemon'], d['challenger']['fast'],  d['challenger']['charged1'],  d['challenger']['charged2'])
    url = "%s/%s/%s-%s-%s-%s-%s-%s-%s-%s/%s%s/%s-%s-%s/%s-%s/" % (
      'https://pvpoke.com/battle/multi/1500',
      self.cup,
      d['pokemon'].lower(),
      d['level'],
      d['atk'], d['def'], d['sta'],
      self.matk, self.mdef,
      int(d['challenger']['bait']),
      d['challenger']['shield'], d['challenger']['shield'],
      moves[0], moves[1], moves[2],
      self.opponent['shields'],
      int(self.opponent['bait'])
      )
    return url

  def fetch_url(self, url, pokemon):
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', '/data/')
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    driver = webdriver.Remote(
      browser_profile=profile,
      command_executor='http://selenium-firefox:4444/wd/hub',
      desired_capabilities=DesiredCapabilities.FIREFOX)
    driver.set_window_size(1024, 2000)
    driver.get(url)
    driver.set_page_load_timeout(30)
    driver.maximize_window()
    logging.info(url)
    driver.save_screenshot("/data/screenshot.png")
    element = driver.find_element_by_xpath("//*[contains(@class, 'download-csv')]")
    results = element.click()
    driver.quit()
    os.chdir("/data/")
    files = filter(os.path.isfile, os.listdir("/data/"))
    files = [os.path.join("/data/", f) for f in files]
    files.sort(key=lambda x: os.path.getmtime(x))
    newest_file = files[-1]
    if newest_file.endswith(".csv"):
      os.rename(newest_file, "%s_%s.csv" % (pokemon.lower(), self.cup.lower()))


class visualize():
  def __init__(self):
    self.data = self._data()

  def _data(self):
    self.node_data = []
    self.edge_data = []
    try:
      file = request.files['json_file']
      d = file.read().decode('utf-8')
      self.data = json.loads(d)
      sim = simulations(self.data)
      self.edge_data = sim.edge_data
      self.node_data = sim.node_data
    except Exception as e:
      traceback.print_exc()
      logging.info(e)
    return d

  def _graph(self):
    try:
        counter = {}
        net = Network(height="100%", width="70%", bgcolor="white", font_color="white")
        net.force_atlas_2based(gravity=-231, central_gravity=0.045, spring_length=135, spring_strength=0.295, damping=1, overlap=1)
        for entry in self.node_data:
          src = entry['challenger_id']
          pokemon = entry['challenger']
          t = "00"
          logging.info(pokemon)
          if re.match(r'.*alolan.*', pokemon.lower()):
            logging.info("Matched alolan")
            t = "61"
          my_img = '/static/icons/pokemon_icon_%s_%s.png' % (f'{src:03}', t)
          logging.info(my_img)

          net.add_node(src, ' ', image=my_img, shape='circularImage', size=50)
        limit = int(request.form['limit'])
        data = json.loads(self.data)
        for entry in self.edge_data:
            src = entry['challenger_id']
            pokemon = entry['challenger']
            opponent = entry['opponent']
            if opponent.lower() in data['settings']['exclude']:
              logging.info("Excluding %s" % opponent)
              continue
            if src not in counter:
              counter[src] = 0
            if counter[src] > limit:
              continue
            dst = entry['opponent_id']
            w = entry['weight']

            t = "00"
            if re.match(r'.*alolan.*', opponent.lower()):
                t = "61"
            opp_img = '/static/icons/pokemon_icon_%s_%s.png' % (f'{dst:03}', t)
            net.add_node(dst, ' ', image=opp_img, shape='circularImage', size=35)
            net.add_edge(src, dst, value=w, arrows='to', arrowStrikethrough=False, smooth=True, color=entry['color'])
            counter[src] = counter.get(src, 0) + 1

        net.set_edge_smooth('dynamic')
        net.show_buttons(filter_=['physics'])
        net.save_graph("/app/templates/test.html")
        time.sleep(5)
        return render_template("test.html")
    except Exception as e:
      traceback.print_exc()
      logging.info(e)

@app.route('/display', methods=['POST'])
def display():
  o = visualize()
  return o._graph()
#  return o._graph()

@app.route('/')
def default():
  return render_template("index.html")


