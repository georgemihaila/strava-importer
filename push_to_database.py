from stravalib.client import Client
from requests import request
import csv
import time
import json
import jsonpickle
from dateutil import parser
import configparser
import pymssql

config = configparser.ConfigParser()
config.read('config.ini')
db = config['database']

conn = pymssql.connect(db['server'], db['user'], db['password'], db['database'])

client = Client()
credentials = config['credentials']
client.client_id = credentials['client_id']
client.access_token = credentials['access_token']
client.refresh_token = credentials['refresh_token']
client.code = credentials['code']

def get_json_value_or_default(entry, key):
    if key in entry.keys():
        return jsonpickle.encode(entry[key].data)
    return jsonpickle.encode({})

def activity_exists(id):
    c1 = conn.cursor()
    c1.execute('SELECT COUNT(*) FROM [dbo].[StravaImports] WHERE [ID] = {}'.format(id))
    count = c1.fetchall()[0][0]
    return count > 0

for activity in client.get_activities():
    id = activity.id % 2147483647
    if not activity_exists(id):

        types = config['data']['import'].split(',')
        streams = client.get_activity_streams(activity.id, types=types)

        c = conn.cursor()
        c.execute("""INSERT INTO [dbo].[StravaImports] 
                    ([ID], [Type], [Name], [StartDate], [Time], [Distance], [AverageSpeed], [AverageHeartRate], 
                    [TimeData], [PositionData], [DistanceData], [AltitudeData], [VelocityData], [HeartRateData], [CadenceData], [WattsData], [TemperatureData], [MovingData], [SmoothGradeData]) 
                    VALUES (%d, %s, %s, CAST(%s as DATETIME2), CAST(%s as DATETIME2), %d, %d, %d,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",

        (id,
        activity.type,
        activity.name,
        parser.parse(str(activity.start_date)),
        parser.parse("2021-04-16T" + str(activity.elapsed_time).replace(' ', 'T')),
        float(activity.distance),
        float(activity.average_speed),
        float(0 if activity.average_heartrate is None else activity.average_heartrate),
            
        get_json_value_or_default(streams, 'time'),
        get_json_value_or_default(streams, 'latlng'),
        get_json_value_or_default(streams, 'distance'),
        get_json_value_or_default(streams, 'altitude'),
        get_json_value_or_default(streams, 'velocity_smooth'),
        get_json_value_or_default(streams, 'heartrate'),
        get_json_value_or_default(streams, 'cadence'),
        get_json_value_or_default(streams, 'watts'),
        get_json_value_or_default(streams, 'temp'),
        get_json_value_or_default(streams, 'moving'),
        get_json_value_or_default(streams, 'grade_smooth'))
        )
        conn.commit()
        print('Imported {}'.format(id))

    else:
        print('{} already exists'.format(id))
    
    time.sleep(9 * 2) #Rate limited to 100 requests every 15 minutes (1 request / 9 seconds)