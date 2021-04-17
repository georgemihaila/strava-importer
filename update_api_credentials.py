from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from urllib import parse
import configparser
import jsonpickle

config = configparser.ConfigParser()
config.read('config.ini')

settings = config['autoimportsettings']

driver = webdriver.Remote(command_executor=settings['seleniumhublocation'],
    desired_capabilities={'browserName': 'chrome', 'javascriptEnabled': True})

driver.get('https://strava.com/login')

driver.find_element_by_id("email").send_keys(settings['strava_username'])
driver.find_element_by_id("password").send_keys(settings['strava_password'])
driver.find_element_by_id("login-button").click()

driver.get(settings['strava_oauth_server_location'])
driver.find_element_by_xpath('/html/body/div/p[2]/a/img').click()

element = WebDriverWait(driver, 10).until(
    lambda x: x.find_element_by_xpath("/html/body/pre"))

data = jsonpickle.decode(element.text)

code = dict(parse.parse_qsl(parse.urlsplit(driver.current_url).query))['code']
print('Code: {}'.format(code))
print(data)

def set_value_in_property_file(section, key, value):
    file_path = 'config.ini'
    config = configparser.RawConfigParser()
    config.read(file_path)
    config.set(section,key,value)                         
    cfgfile = open(file_path,'w')
    config.write(cfgfile, space_around_delimiters=False)  # use flag in case case you need to avoid white space.
    cfgfile.close()

    
set_value_in_property_file('credentials', 'access_token', data['access_token'])
set_value_in_property_file('credentials', 'refresh_token', data['refresh_token'])
set_value_in_property_file('credentials', 'code', code)

driver.close()