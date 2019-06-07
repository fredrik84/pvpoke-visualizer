# import libraries
import urllib.request
from bs4 import BeautifulSoup

# specify the url
urlpage = 'https://pvpoke.com/battle/multi/1500/rainbow/venusaur-25-10-10-10-4-4-1/11/2-1-3/1-1/' 
print(urlpage)

driver = webdriver.Firefox()
# get web page
driver.get(urlpage)
# execute script to scroll down the page
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
# sleep for 30s
time.sleep(30)
# driver.quit()
results = driver.find_elements_by_xpath("//*[@class='button download-csv']")
print('Number of results', len(results))
