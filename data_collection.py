from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import time
import datetime
import csv

ts = time.time()
# UTC + 8
ts = ts - 28800 
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')
ed = datetime.datetime.fromtimestamp(ts-10).strftime('%Y-%m-%dT%H:%M:%S')
st = st + ".000Z"
ed = ed + ".000Z"
print("end time: " + st)
print("start time: " + ed)

#field_name_list = ['filesystem']
field_name_list = ['core','cpu','diskio','entropy','filesystem','fsstat', \
    'total_size','load','memory','actual','swap','page_stats','hugepages', \
    'swap.out','network','network_summary','process','cpu','memory','fd', \
    'cgroup','cpu','cpuacct','memory','blkio','process.summary','raid','service', \
    'resources','network','socket','socket.summary','all','tcp','all','udp','all','uptime','users']

client = Elasticsearch([{'host': 'localhost', 'port': 9200}])
index_name = 'metricbeat'


for field_name in field_name_list:
    #using Elasticsearch DSL
    s = Search(using=client, index=index_name+"-*") \
       .query('match', event__dataset='system.'+field_name) \
       .query('range',**{'@timestamp': {'gte':ed, 'lt':st, 'format':'strict_date_optional_time'}})

    def get_all_value(nest_dict,temp,a):
        for key, value in nest_dict.items():
            if type(value) is dict:
                get_all_value(value, key+".",a)
            else:
                a[str(temp) + str(key)] = str(value)
    b = {}
    for hit in s.scan():
        hit = hit.to_dict()
        get_all_value(hit['system'][field_name],"",b)

    #use scan to access all the document (default display size=10)
    filename = field_name + '.csv'
    with open(filename, 'w') as csvfile:
        # Define attribute name
        fieldnames = ['timestamp'] + list(b.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)        
        # Write first row name
        writer.writeheader()
        a = {}
        for hit in s.scan():
            a['timestamp'] = hit['@timestamp'][:-6]
            hit = hit.to_dict()
            get_all_value(hit['system'][field_name],"",a)
            writer.writerow(a)
