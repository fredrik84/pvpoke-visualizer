#!/usr/bin/python3
from argparse import ArgumentParser
import json
import requests

parser = ArgumentParser()
parser.add_argument('-b', '--baiting', default=1, type=int)
parser.add_argument('-a', '--address', default="localhost:8000")
args = parser.parse_args()
d = {
    "settings": {
        "cup": "jungle",
        "my_shield": 0,
        "op_shield": 0,
        "my_bait": args.baiting,
        "op_bait": args.baiting,
        "op_charges": 2,
    },
    "data": [
        {"pokemon": "forretress", "fast": "Bug Bite", "charged1": "Heavy Slam", "charged2": "Earthquake"},
        {"pokemon": "vigoroth", "fast": "Counter", "charged1": "Body Slam", "charged2": "Bulldoze"},
        {"pokemon": "golem_alolan", "fast": "Rock Throw", "charged1": "Rock Blast", "charged2": "Wild Charge"},
        {"pokemon": "noctowl", "fast": "Wing Attack", "charged1": "Sky Attack", "charged2": "Night Shade"},
        {"pokemon": "graveler_alolan", "fast": "Rock Throw", "charged1": "Rock Blast", "charged2": "Thunderbolt"},
        {"pokemon": "magnezone", "fast": "Spark", "charged1": "Wild Charge", "charged2": "Flash Cannon"},
        {"pokemon": "scizor", "fast": "Fury Cutter", "charged1": "X_Scissor", "charged2": "Iron Head"},
        {"pokemon": "magneton", "fast": "Thunder Shock", "charged1": "Discharge", "charged2": "Magnet Bomb"},
        {"pokemon": "venusaur", "fast": "Vine Whip", "charged1": "Frenzy Plant", "charged2": "Sludge Bomb"},
        {"pokemon": "vespiquen", "fast": "Bug Bite", "charged1": "X_Scissor", "charged2": "Power Gem"},
        {"pokemon": "pidgeot", "fast": "Wing Attack", "charged1": "Aerial Ace", "charged2": "Brave Bird"},
        {"pokemon": "venomoth", "fast": "Confusion", "charged1": "Silver Wind", "charged2": "Poison Fang"},
        {"pokemon": "raichu", "fast": "Thunder Shock", "charged1": "Wild Charge", "charged2": "Brick Break"},
        {"pokemon": "cradily", "fast": "Infestation", "charged1": "Grass Knot", "charged2": "Stone Edge"},
        {"pokemon": "beedrill", "fast": "Poison Jab", "charged1": "X_Scissor", "charged2": "Sludge Bomb"},
        {"pokemon": "lanturn", "fast": "Water Gun", "charged1": "Thunderbolt", "charged2": "Hydro Pump"},
        {"pokemon": "heracross", "fast": "Counter", "charged1": "Megahorn", "charged2": "Close Combat"},
        {"pokemon": "masquerain", "fast": "Air Slash", "charged1": "Silver Wind", "charged2": "Ominous Wind"},
        {"pokemon": "scyther", "fast": "Air Slash", "charged1": "Aerial Ace", "charged2": "X_Scissor"}
    ]
}

for i in range(0, 3):
  for j in range(0, 3):
    d['settings']['my_shield'] = i
    d['settings']['op_shield'] = j
    r = requests.post("http://%s/admin-hidden-stuff" % args.address, data={'json': json.dumps(d)})
