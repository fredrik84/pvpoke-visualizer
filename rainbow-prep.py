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
        "cup": "rainbow",
        "my_shield": 0,
        "op_shield": 0,
        "my_bait": args.baiting,
        "op_bait": args.baiting,
        "op_charges": 2,
    },
    "data": [
        { "charged1": "Rock Tomb", "charged2": "Earthquake", "pokemon": "forretress", "fast": "Bug Bite" },
        { "charged1": "Frenzy Plant","charged2": "Sludge Bomb", "pokemon": "venusaur", "fast": "Vine Whip"},
        { "charged1": "Outrage", "charged2": "Hydro Pump", "pokemon": "kingdra", "fast": "Dragon Breath" },
        { "charged1": "Earthquake", "charged2": "Stone Edge", "pokemon": "quagsire", "fast": "Mud Shot" },
        { "charged1": "Frenzy Plant", "charged2": "Earthquake", "pokemon": "meganium", "fast": "Vine Whip"},
        { "charged1": "Blast Burn", "charged2": "Solar Beam", "pokemon": "typhlosion", "fast": "Shadow Claw" },
        { "charged1": "Psyshock", "charged2": "Solar Beam", "pokemon": "ninetales", "fast": "Fire Spin" },
        { "charged1": "Blast Burn", "charged2": "Dragon Claw", "pokemon": "charizard", "fast": "Fire Spin" },
        { "charged1": "Leaf Blade", "charged2": "Sludge Bomb", "pokemon": "victreebel", "fast": "Razor Leaf" },
        { "charged1": "Thunderbolt", "charged2": "Hydro Pump", "pokemon": "lanturn", "fast": "Water Gun" },
        { "charged1": "Seed Bomb", "charged2": "Psychic", "pokemon": "exeggutor", "fast": "Confusion" },
        { "charged1": "Aerial Ace", "charged2": "Ice Beam", "pokemon": "mantine", "fast": "Wing Attack" },
        { "charged1": "Wild Charge", "charged2": "Thunder Punch", "pokemon": "raichu", "fast": "Thunder Shock" },
        { "charged1": "Megahorn", "charged2": "Earthquake", "pokemon": "heracross", "fast": "Counter" },
        { "charged1": "Ice Beam", "charged2": "Play Rough", "pokemon": "azumarill", "fast": "Bubble" },
        { "charged1": "Sludge Bomb", "charged2": "Power Whip", "pokemon": "ivysaur", "fast": "Vine Whip" },
        { "charged1": "X_Scissor", "charged2": "Sludge Bomb", "pokemon": "beedrill", "fast": "Poison Jab" },
        { "charged1": "Stone Edge", "charged2": "Overheat", "pokemon": "magcargo", "fast": "Rock Throw" },
        { "charged1": "Discharge", "charged2": "Magnet Bomb", "pokemon": "magneton", "fast": "Thunder Shock" },
        { "charged1": "Silver Wind", "charged2": "Poison Fang", "pokemon": "venomoth", "fast": "Confusion" }
    ]
}

for i in range(0, 3):
  for j in range(0, 3):
    d['settings']['my_shield'] = i
    d['settings']['op_shield'] = j
    r = requests.post("http://%s/admin-hidden-stuff" % args.address, data={'json': json.dumps(d)})
