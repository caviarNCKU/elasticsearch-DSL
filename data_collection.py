from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import time
import datetime
import csv
import requests
import pandas as pd
from bs4 import BeautifulSoup

# web information parsing
url = "https://www.elastic.co/guide/en/beats/metricbeat/current/exported-fields-system.html"
resp = requests.get(url)
soup = BeautifulSoup(resp.text, 'html.parser')
dt = soup.find_all("dt")
dd = soup.find_all("dd")

T = []
for x in range(len(dt)):
    s = []
    for y in dt[x].find_all('strong'):
        s.append(y.get_text())
    T.append(s)

for x in range(len(dd)):
    for y in dd[x].find_all('p'):
        T[x].append(y.get_text())

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')
#ed = datetime.datetime.fromtimestamp(ts-28810).strftime('%Y-%m-%dT%H:%M:%S')
ed = datetime.datetime.fromtimestamp(ts-28810-28800).strftime('%Y-%m-%dT%H:%M:%S')
print(st)
print(ed)
'''
field_name_list = ['core','cpu','diskio','entropy','filesystem','fsstat', \
    'total_size','load','memory','actual','swap','page_stats','hugepages', \
    'swap.out','network','network_summary','process','cpu','memory','fd', \
    'cgroup','cpu','cpuacct','memory','blkio','raid','service', \
    'resources','network','socket','socket.summary','all','tcp','all','udp','all','uptime','users']
'''

field_name_list = ['cpu','diskio','memory', 'network']    
#field_name_list = ['memory']  

client = Elasticsearch([{'host': 'localhost', 'port': 9200}])
#field_name = 'load'
index_name = 'metricbeat'



for field_name in field_name_list:
    #using Elasticsearch DSL
    s = Search(using=client, index=index_name+"-*") \
        .query('match', event__dataset='system.'+field_name) \
        .filter('range',**{'@timestamp': {'gte':ed, 'lt':st, 'format':'strict_date_optional_time'}})
    print(s)    
    def get_all_value(nest_dict,temp,a):
        for key, value in nest_dict.items():
            res = temp
            if type(value) is dict:
                temp = temp + key + "."
                get_all_value(value, temp , a)
            else:
                a["system."+ field_name + "." + str(temp) + str(key)] = str(value)
            temp = res
    b = {}
    for hit in s[0:1]:
        hit = hit.to_dict()
        get_all_value(hit['system'][field_name],"",b)

    #use scan to access all the document (default display size=10)
    filename = field_name + '.csv'
    with open(filename, 'a') as csvfile:
        # Define attribute name
        abc = []
        fieldnames = ['timestamp'] +['hostname']+ b.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)        
        # Write first row name
        writer.writeheader()
        a = {}
        for hit in s.scan():
            #print (hit['host']['name'])
            abc = hit['@timestamp'].replace("Z", '')
            abc = str(abc).replace("T", ' ')
            abc = str(abc).replace("+08:00",'')
            abc = abc[:-4]
            a['timestamp'] = str(abc) #hit['@timestamp']
            hit = hit.to_dict()
            get_all_value(hit['system'][field_name],"",a)
            a['hostname'] = hit['host']['name']
            writer.writerow(a)
    df = pd.read_csv(filename)
    origin_name = df.columns
    rename = ['timestamp', 'hostname']
    for key, value in enumerate(origin_name):
        if key > 1:
            for list_ in T:
                if list_[0] == value:
                    if len(list_) == 4:
                        name = list_[0] + " " + list_[2] + " " + list_[3]
                        rename.append(name)
                    else:
                        name = list_[0] + " " + list_[2]
                        rename.append(name)
    df.columns = rename
    df.to_csv(filename)