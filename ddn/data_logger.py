#@@---------------------------@@
#  Author: Chamil Jayasundara
#  Date: 5/18/17
#  Description:
#@@---------------------------@@

from mininet.log import setLogLevel, info, lg
import sys
import logging
import subprocess

class Logger(object):
    def __init__(self, terminal, filename):
        self.terminal = terminal
        self.log = filename
        with open(self.log, 'w') as f:
            f.write("****CONSOLE OUTPUT****" + '\n\n\n')


    def write(self, message):
        self.terminal.write(message)
        with open(self.log, 'a') as f:
            f.write(message + '\n')

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass

def log_to_file(file_name):
    with open(file_name, 'w') as f:
        f.write("****LOG OUTPUT****" + '\n\n\n')

    fh = logging.FileHandler(file_name)
    setLogLevel('info')
    lg.addHandler(fh)

def start_logging():
    ##Copy config file
    subprocess.call(['cp' , './configs.json', './data/PARAMS/'])

    ##Redirect python logger to a file
    log_to_file('data/PARAMS/output.log')

    ##Redirect Stout to a file
    sys.stdout = Logger(sys.stdout, "data/PARAMS/console.log")