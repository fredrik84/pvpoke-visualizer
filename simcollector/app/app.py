#!/usr/bin/python3
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

d = {
    'cup': 'rainbow',
    'pokemon': 'venusaur',
    'level': 25,
    'atk': 10,
    'def': 10,
    'sta': 10,
    'matk': 4,
    'mdef': 4,
    'challenger': {
        'bait': True,
        'shield': 1,
        'fast': 'Vine Whip',
        'charged1': 'Frenzy Plant',
        'charged2': 'Sludge Bomb',
        },
    'opponent': {
        'shield': 1,
        'bait': True,
        }
    }

gamemaster = json.load(open('gamemaster.json'))

def get_moves(pokemon,fast,charged1,charged2=None):
    fast = fast.upper().replace(" ", "_")
    charged1 = charged1.upper().replace(" ", "_")
    if charged2:
        charged2 = charged2.upper().replace(" ", "_")

    movelist = []
    for entry in gamemaster['pokemon']:
        if entry['speciesId'].lower() == pokemon:
            pprint.pprint(entry)
            movelist.append(str(entry['fastMoves'].index(fast)+1))
            movelist.append(str(entry['chargedMoves'].index(charged1)+1))
            if charged2:
                movelist.append(str(entry['chargedMoves'].index(charged2)+1))
            else:
                movelist.append(str(0))
            break
    return movelist

def generate_url(d):
    moves = get_moves(d['pokemon'], d['challenger']['fast'],  d['challenger']['charged1'],  d['challenger']['charged2'])
    url = "%s/%s/%s-%s-%s-%s-%s-%s-%s-%s/%s%s/%s-%s-%s/%s-%s/" % (
        'https://pvpoke.com/battle/multi/1500',
        d['cup'],
        d['pokemon'],
        d['level'],
        d['atk'], d['def'], d['sta'],
        d['matk'], d['mdef'],
        int(d['challenger']['bait']),
        d['challenger']['shield'], d['challenger']['shield'],
        moves[0], moves[1], moves[2],
        d['opponent']['shield'],
        int(d['opponent']['bait'])
        )

    return url

def fetch_url(url):
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', '/data/')
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    driver = webdriver.Remote(
      ¦ ¦ ¦ ¦ browser_profile=profile,
      ¦ ¦ ¦ ¦ command_executor='http://localhost:4444/wd/hub',
      ¦ ¦ ¦ ¦ desired_capabilities=DesiredCapabilities.FIREFOX)

    driver.set_window_size(1024, 2000)
    driver.get(url)
    driver.maximize_window()
    element = driver.find_element_by_xpath("//*[contains(@class, 'download-csv')]")
    results = element.click()
    driver.quit()


url = generate_url(d)
fetch_url(url)

