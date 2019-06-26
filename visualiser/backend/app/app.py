#!/usr/bin/python3
from pyvis.network import Network
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
from backports import csv
import hashlib
import logging
import traceback
import time
import memcache
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)-8s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

stats = json.load(open("stats.txt"))
mc = memcache.Client(['memcached-visualiser:11211'], debug=0)

class simulations():
  def __init__(self, entry):
    self.gamemaster = json.load(open('/app/gamemaster.json'))
    # Write stuff to handle the "not combined" json format (missing matk,mdef,opponent and so on)
    self.cup = entry['settings']['cup']
    self.opponent = {
            'my_shield': entry['settings']['my_shield'],
            'op_shield': entry['settings']['op_shield'],
            'my_bait': entry['settings']['my_bait'],
            'op_bait': entry['settings']['op_bait'],
            'op_charges': entry['settings']['op_charges']
            }
    self.node_data = []
    self.edge_data = []
    for e in entry['data']:
        self.url = self._generate_url(e)
        d = mc.get(self.url)
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
    try:
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
          logging.info('Adding %s to list of pokemons' % challenger)
          for entry in sorted_result:
            opponent = entry[0].lower().title().replace("(", "").replace(")", "").replace(" ", "_").replace("'", "").lower().title()
            if opponent not in stats:
                logging.info("%s was not found in stats table" % opponent)
                continue
            if int(entry[2]) > 0:
                self.edge_data.append({
                  'challenger': challenger,
                  'challenger_id': stats[challenger],
                  'opponent': opponent,
                  'opponent_id': stats[opponent],
                  'weight': int(entry[2])/100,
                  'color': color})
        mc.set(self.url, json.dumps({'edge': self.edge_data, 'node': self.node_data}))
        return True
    except Exception as e:
      traceback.print_exc()
      logging.info(e)

  def _get_moves(self, pokemon,fast,charged1,charged2=None):
    fast = fast.upper().replace(" ", "_")
    charged1 = charged1.upper().replace(" ", "_")
    if charged2:
        charged2 = charged2.upper().replace(" ", "_")

    movelist = []
    for entry in self.gamemaster['pokemon']:
      if entry['speciesId'].lower() == pokemon.lower():
        movelist.append(str(entry['fastMoves'].index(fast)+0))
        movelist.append(str(entry['chargedMoves'].index(charged1)+1))
        if charged2:
          movelist.append(str(entry['chargedMoves'].index(charged2)+1))
        else:
          movelist.append(str(0))
        break
    return movelist

  def _generate_url(self, d):
    moves = self._get_moves(d['pokemon'], d['fast'],  d['charged1'], d['charged2'])
    url = "%s/%s/%s/%s%s/%s-%s-%s/%s-%s/" % (
      'https://pvpoke.com/battle/multi/1500',
      self.cup,
      d['pokemon'].lower(),
      self.opponent['my_shield'], self.opponent['op_shield'],
      moves[0], moves[1], moves[2],
      self.opponent['op_charges'], self.opponent['op_bait']
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
    time.sleep(5)
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
  def __init__(self, config):
    self.config = config
    self.data = self._data()

  def _data(self):
    logging.info("Creating graph data")
    self.node_data = []
    self.edge_data = []
    try:
      sim = simulations(self.config)
      self.include = []
      for entry in self.data['data']:
          self.include.append(entry['pokemon'])
      self.edge_data = sim.edge_data
      self.node_data = sim.node_data
    except Exception as e:
      traceback.print_exc()
      logging.info(e)
    return d

  def _graph(self):
    try:
        counter = {}
        net = Network(height="100%", width="100%", bgcolor="white", font_color="white")
        net.force_atlas_2based(gravity=-250, central_gravity=0.005, spring_length=0, spring_strength=0, damping=1, overlap=1)
        exists = []
        for entry in self.edge_data:
            src = entry['challenger_id']
            pokemon = entry['challenger']
            if src in exists:
                continue
            t = "00"
            if 'alolan' in pokemon.lower():
                t = "61"
            my_img = '/static/icons/pokemon_icon_%s_%s.png' % (f'{src:03}', t)
            net.add_node(src, ' ', image=my_img, shape='circularImage', size=50, color={'highlight': {'border': entry['color']}}, borderWidthSelected=5)
            exists.append(src)

        for entry in self.edge_data:
            src = entry['challenger_id']
            pokemon = entry['challenger']
            opponent = entry['opponent']
            if opponent.lower() not in self.include:
                continue
            dst = entry['opponent_id']
            w = entry['weight']/10
            net.add_edge(src, dst, value=w, arrows='to', arrowStrikethrough=False, smooth=True, color={"color": entry['color'], "highlight": entry['color'], "opacity": 0.05}, selfReferenceSize=50)

        net.set_edge_smooth('continuous')
        net.show_buttons(filter_=['physics'])
        net.save_graph("/app/static/%svs%s.html" % (self.config['settings']['my_shield'], self.config['settings']['op_shield']))
        return True
    except Exception as e:
      traceback.print_exc()
      logging.info(e)

while True:
    logging.info("Updating simulations")
    start = time.time()
    data = mc.get('simulation_keys')
    if data:
        for key in json.loads(data):
            config = json.loads(mc.get('%s_config' % key))
            vis = visualize(config)
            vis._graph()
            del vis
    else:
        logging.warning("Memcached key 'simulation_keys' is empty or does not exist")

    time.sleep(600-(time.time()-start))
