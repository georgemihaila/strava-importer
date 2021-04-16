from stravalib.client import Client
from requests import request
import time
import configparser
import csv
import json

config = configparser.ConfigParser()
config.read('config.ini')
credentials = config['credentials']

client = Client()
client.client_id = credentials['client_id']
client.access_token = credentials['access_token']
client.refresh_token = credentials['refresh_token']
client.code = credentials['code']

all_data = []
for activity in client.get_activities():
    data = {}
    data['activity'] = str(activity)
    types = config['data']['import'].split(',')
    streams = client.get_activity_streams(activity.id, types=types)
    for t in types:
        if t in streams.keys():
            data[t] = streams[t].data
    print('Imported {}'.format(activity.id))
    all_data.append(data)

    time.sleep(9 * 2) #Rate limited to 100 requests every 15 minutes (1 request / 9 seconds)

with open('all_data.json', 'w') as outfile:
    json.dump(all_data, outfile)

print('Wrote data to all_data.json')