#@@---------------------------@@
#  Author: Chamil Jayasundara
#  Date: 5/18/17
#  Description:
#@@---------------------------@@

import json
import requests
from requests.auth import HTTPBasicAuth
import collections
import ast
import datetime
import time


"""This is to query data from the TSDR"""

class TSDRqueryPasser:

    def __init__(self, controller):
        self.url = 'http://' + controller['ip'] + ':' + str(controller['port']) \
                   + '/tsdr/'
        self.credential = controller['api_credentials']

    def __query_data(self, data_type, metric_name, start_time='', end_time='', node_id='', data_category='', record_key=''):
        url = self.url + data_type + '/query'
        tsdrkey = "[NID" + node_id + "=][DC" + data_category + "=][MN=" + metric_name + "][RK=" + record_key + "]"
        parameters = {'tsdrkey':tsdrkey, 'from':start_time, 'until': end_time}

        return requests.get(url, params=parameters,
                            auth=HTTPBasicAuth(self.credential['uname'], self.credential['pwd']))



    def get_data(self, metric, start_time, end_time, write_to_file=False, **kwargs):

        # metric types: EXTERNAL, FLOWSTATS, FLOWTABLESTATS, NETFLOW, PORTSTATS,

        if metric == 'NETFLOW':
            data_type = 'logs'

        else:
            data_type = 'metrics'

        r = self.__query_data(data_type, metric,
                              start_time=start_time, end_time=end_time, **kwargs)

        if write_to_file:
            filename = 'data/' + metric + '/' + metric + '_' + start_time + '_' + end_time + '.log'
            with open(filename, 'w') as outfile:
                outfile.write(r.text)


        return r

class Logger(object):
    def __init__(self, terminal):
        self.terminal = terminal
        self.log = "data/PARAMS/console.log"
        with open(self.log, 'w') as f:
            f.write("****CONSOLE LOG****" + '\n\n\n')


    def write(self, message):
        self.terminal.write(message)
        with open(self.log, 'a') as f:
            f.write(message + '\n')

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass

"""This is to get the config file from json format to the format required"""
def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

def get_config(config_file):
    with open(config_file) as file:
        config = json_load_byteified(file)

    return config


def write_time(message, start_empty = False ):
    filename = 'data/PARAMS/setup.log'
    if start_empty:
        print message + ' at: ' + str(datetime.datetime.now()) + '\n'
        # with open(filename, 'w') as myfile:
        #     myfile.write(message + ' at: ' + str(datetime.datetime.now()) + '\n')

    else:
        print message + ' at: ' + str(datetime.datetime.now()) + '\n'
        # with open(filename, "a") as myfile:
        #     myfile.write(message + ' at: ' + str(datetime.datetime.now()) + '\n')



# if the script is run directly (sudo custom/optical.py):
if __name__ == '__main__':
    tsdr = TSDRqueryPasser({'ip':'127.0.0.1', 'port':8181, 'api_credentials': {'uname':'admin', 'pwd':'admin'}})
    # tsdr.get_data('NETFLOW', '0', '240000000000', write_to_file=True)
    metrics = ['EXTERNAL', 'FLOWSTATS', 'FLOWTABLESTATS', 'NETFLOW', 'PORTSTATS']
    #
    for m in metrics:
        tsdr.get_data(m, '0', '240000000000', write_to_file=True)


            # metric types: EXTERNAL, FLOWSTATS, FLOWTABLESTATS, NETFLOW, PORTSTATS,