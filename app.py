#!/usr/bin/python3
from pyvis.network import Network
import matplotlib.image as mpimg
import json
import pprint
from flask import Flask
from flask import render_template
from flask import request
from flask import abort
import csv
import hashlib

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
stats = json.load(open("stats.txt"))


class visualize():
  def __init__(self):
    self.data = self._data()

  def _data(self):
    self.node_data = []
    self.edge_data = []
    try:
      for n in range(1,7):
        file = request.files['p%s_file' % n]
        contents = file.read()
        result = [row for row in csv.reader(contents.decode('utf-8').splitlines(), delimiter=',')]
        result.pop(0)
        sorted_result = sorted(result, key=lambda x: x[1])[::-1]
        limit = int(request.form['limit'])
        print('Limit is %s' % limit)
        d = []
        challenger = request.form['p%s' % n].lower().title()
        self.node_data.append({"challenger": challenger, 'challenger_id': stats[challenger]})
        hasher = hashlib.md5()
        hasher.update(challenger.encode('utf-8'))
        color = "#" + hasher.hexdigest()[:6]
        for entry in sorted_result[:limit]:
          opponent = entry[0].lower().title()
          self.edge_data.append({
            'challenger': challenger,
            'challenger_id': stats[challenger],
            'opponent': opponent,
            'opponent_id': stats[opponent],
            'weight': int(entry[1])/1000,
            'color': color})
    except Exception as e:
      print(e)
    return True

  def _graph(self):
    data = self.data
    #data = json.load(open("rankings-1500.json"))
    net = Network(height="100%", width="70%", bgcolor="white", font_color="white")
    net.force_atlas_2based(gravity=-231,central_gravity=0.045,spring_length=135,spring_strength=0.295,damping=1,overlap=1)
    for entry in self.node_data:
      src = entry['challenger_id']
      pokemon = entry['challenger']
      my_img = '/static/icons/pokemon_icon_%s_00.png' % f'{src:03}'

      net.add_node(src, ' ', image=my_img, shape='circularImage', size=50)

    for entry in self.edge_data:
        src = entry['challenger_id']
        dst = entry['opponent_id']
        w = entry['weight']
        pokemon = entry['challenger']
        opponent = entry['opponent']
        opp_img = '/static/icons/pokemon_icon_%s_00.png' % f'{dst:03}'
        net.add_node(dst, ' ', image=opp_img, shape='circularImage', size=35)
        net.add_edge(src, dst, value=w, arrows='to', arrowStrikethrough=False, smooth=True, color=entry['color'])

    net.set_edge_smooth('dynamic')
    net.show_buttons(filter_=['physics'])
    net.save_graph("templates/test.html")
    return render_template("test.html")

@app.route('/display', methods=['POST'])
def display():
  o = visualize()
  return o._graph()

@app.route('/')
def default():
  return render_template("index.html")


