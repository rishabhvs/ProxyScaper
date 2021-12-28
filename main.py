from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep,strftime
import requests
import threading
import sys

uptime = 90 

options = Options()
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

print('Proxy Scraping Started from www.freeproxylists.net\n')
curr_dir = __file__.rsplit('\\', 1)[0]
proxyList = []
done=0
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

print('Scraped {} Proxies. Proxy Testing Started.\nNOTE: These Proxies Do Not Gaurantee Anonymity.\n'.format(len(proxyList)))
driver.quit()

def test(s):
    global done
    for i in range(s,len(proxyList),5):
        if(s==3):
            count()
        proxy=proxyList[i]
        try:
            response = requests.get(url, proxies={"http": proxy, "https": proxy},timeout=10)
            if(response.json()['origin'] in proxy):
                working.append(proxy)
        except Exception as e:
            pass
        done+=1
        if(s==3):
            count()
            
def count():
    global done
    sys.stdout.write("\rTested {} of {}".format(done,len(proxyList)))
    sys.stdout.flush()

url = 'https://httpbin.org/ip'
working=[]
threading_list=[]
for i in range(5): # Start 5 Threads to Check proxy working status
    threading_list.append(threading.Thread(target=test,args=(i,)))
    threading_list[i].start()

for t in threading_list:
    t.join()
filename = curr_dir+"/proxies-"+strftime("%Y%m%d-%H%M%S")+".txt"
print('\nList of Working Proxies Generated at '+filename)
with open(filename, "w") as f:
    f.writelines('\n'.join(working))
