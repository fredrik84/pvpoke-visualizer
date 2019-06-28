#!/usr/bin/python3
from argparse import ArgumentParser
import json
import requests
import pprint

parser = ArgumentParser()
parser.add_argument('-b', '--baiting', default=1, type=int)
parser.add_argument('-a', '--address', default="localhost:8000")
parser.add_argument('-c', '--cup', required=True)
parser.add_argument('-e', '--extra', default="")
parser.add_argument('-y', '--yes', action='store_true', default=False)
args = parser.parse_args()

r = requests.get("https://pvpoke.com/data/%s/overall/rankings-1500.json" % args.cup)

data = json.loads(r.text)
include = []
for row in data[:20]:
    include.append(row['speciesId'].lower())

for e in args.extra.split(','):
    include.append(e.lower())

subset = data[:20]
pokemons = []
for row in data:
    pokemon = row['speciesId'].lower()
    if pokemon in include: 
        chargedMoves = sorted(row['moves']['chargedMoves'], key=lambda x: x['uses'])[::-1]
        fastMoves = sorted(row['moves']['fastMoves'], key=lambda x: x['uses'])[::-1]
        pokemons.append({
            'pokemon': pokemon, 
            'fast': fastMoves[0]['moveId'], 
            'charged1': chargedMoves[0]['moveId'], 
            'charged2': chargedMoves[1]['moveId']
            })

d = {
    "settings": {
        "cup": "jungle",
        "my_shield": 0,
        "op_shield": 0,
        "my_bait": args.baiting,
        "op_bait": args.baiting,
        "op_charges": 2,
    },
    "data": pokemons
    }

if not args.yes:
    pprint.pprint(d)
else:
    for i in range(0, 3):
      for j in range(0, 3):
        d['settings']['my_shield'] = i
        d['settings']['op_shield'] = j
        r = requests.post("http://%s/admin-hidden-stuff" % args.address, data={'json': json.dumps(d)})
