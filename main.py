import sys
import threading
from time import sleep, strftime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

uptime = '70'

options = Options()
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)


curr_dir = __file__.rsplit('\\', 1)[0]
proxyList = []
url = 'https://httpbin.org/ip'
working = []
threading_list = []
done = 0

print('Proxy Scraping Started from http://www.freeproxylists.net')
driver.get('https://www.freeproxylists.net/?u='+uptime)
sleep(10)  # Delay added incase Captcha Needs to be Solved.
for i in range(1, 10):
    driver.get('https://www.freeproxylists.net/?u='+uptime+'&page='+str(i))
    table = driver.find_element_by_class_name('DataGrid')
    proxyRaw = table.find_elements_by_tag_name('tr')[1:]
    if(len(proxyRaw) == 0):
        break
    for i in range(len(proxyRaw)):
        ele = proxyRaw[i].find_elements_by_tag_name('td')
        if len(ele) < 2:
            continue
        proxyList.append('http://'+ele[0].text+':'+ele[1].text)
driver.quit()

print('Proxy Scraping Started from https://www.proxy-list.download')
for p in requests.get('https://www.proxy-list.download/api/v1/get?type=http').text.split('\r\n') + requests.get('https://www.proxy-list.download/api/v1/get?type=https').text.split('\r\n'):
    proxyList.append('http://'+p)

for u in ['https://us-proxy.org/', 'https://www.sslproxies.org/', 'https://free-proxy-list.net/']:
    print('Proxy Scraping Started from {}'.format(u))
    res = requests.get(u)
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find('table', {'class': 'table'})
    proxyRaw = table.find_all('tr')[1:]
    if(len(proxyRaw) != 0):
        for i in range(len(proxyRaw)):
            ele = proxyRaw[i].find_all('td')
            if len(ele) < 2:
                continue
            proxyList.append('http://'+ele[0].text+':'+ele[1].text)

print('\nTotal Proxies Scraped :', len(proxyList))
proxyList = list(set(proxyList))
print('Unique Proxies :', len(list(proxyList)))
print('\nProxy Testing Started.\nNOTE: These Proxies Do Not Gaurantee Anonymity.\n')


def test(s):
    global done
    for i in range(s, len(proxyList), 50):
        proxy = proxyList[i]
        try:
            response = requests.get(
                url, proxies={"http": proxy, "https": proxy}, timeout=10)
            if(response.json()['origin'] in proxy):
                working.append(proxy)
        except Exception as e:
            pass
        done += 1
        count()


def count():
    global done
    sys.stdout.write("\rTested {} of {}.".format(done, len(proxyList)))
    sys.stdout.flush()


for i in range(50):  # Start 50 Threads to Check proxy working status
    threading_list.append(threading.Thread(target=test, args=(i,)))
    threading_list[i].start()

for t in threading_list:
    t.join()

print('\nlive proxies :',len(working))
filename = curr_dir+"/proxies-"+strftime("%Y%m%d-%H%M%S")+".txt"
print('List of Live Proxies Generated at '+filename)
with open(filename, "w") as f:
    f.writelines('\n'.join(working))
