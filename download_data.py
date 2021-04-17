from stravalib.client import Client
from requests import request
import time
import configparser
import csv
import json

class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

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

    data['id'] = activity.id
    data['name'] = activity.name
    data['start_date'] = activity.start_date
    data['distance'] = float(activity.distance)
    data['time'] = activity.elapsed_time
    data['type'] = activity.type
    data['average_speed'] = float(activity.average_speed)
    data['average_heart_rate'] = activity.average_heartrate

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