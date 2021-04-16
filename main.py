from stravalib.client import Client
from requests import request
import time
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
credentials = config['credentials']

client = Client()
client.client_id = credentials['client_id']
client.access_token = credentials['access_token']
client.refresh_token = credentials['refresh_token']
client.code = credentials['code']
print(client.access_token)

athlete = client.get_athlete()

print(athlete)
for activity in client.get_activities():
    print(activity)
    print(client.get_activity(activity.id))
    types = [ 'time', 'latlng', 'distance', 'altitude', 'velocity_smooth',
    'heartrate', 'cadence', 'watts', 'temp', 'moving', 'grade_smooth' ]
    streams = client.get_activity_streams(activity.id, types=types)
    for t in types:
        if t in streams.keys():
            print(t + " - ")
            print(streams[t].data)
    break