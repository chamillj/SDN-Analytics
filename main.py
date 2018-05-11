#@@---------------------------@@
#  Author: Chamil Jayasundara
#  Date: 5/18/17
#  Description:
#@@---------------------------@@

from mininet.log import setLogLevel, info, lg
from mininet.clean import Cleanup
from ddn.network import MyNetwork, ODL
from ddn.db import Database
from ddn.utils import get_config, write_time
from mininet.cli import CLI
import datetime
import time
from ddn.data_logger import start_logging
import sys
import logging
from multiprocessing import Process
import subprocess
import shutil


# test_duration = 6 * 60*60 # six hours
test_duration = 24 * 60 * 60  # 10 min

# if the script is run directly (sudo custom/optical.py):
if __name__ == '__main__':

    start_logging()

    write_time('starting', start_empty= True)

    ##Clean up
    Cleanup.cleanup()
    db = Database()
    db.delete_content()

    ##Start
    net = MyNetwork(get_config('configs.json'))
    net.start()
    net.enable_netflow(net.switches, net.config['controller']['ip'])
    net.enable_sflow(net.switches, net.config['controller']['ip'], 256, 30)
    net.pingAll() # this is for the discovery
    net.pingAll() #just to make sure everythings working
    int_table = net.print_interface_id() #This will print and log the interface name and corresponding ifaceindex in SFLOW
    net.print_link_info()  # This will print and log the connection information

    h1, h2, h3 = net.get('h1', 'h2', 'h3')

    ########set default gateway
    h1.cmd('route add default gw 10.0.0.3')
    h2.cmd('route add default gw 10.0.0.3')
    h3.cmd('route add default gw 10.0.0.3')


    #Start Traffic
    write_time("Start Replaying traffic")
    h1.cmd('tcpreplay -i h1-eth0 -x 4 --loop 0 --unique-ip /home/chamil/pcap/sm_dm.pcap > tcpreplay.out &')
    h2.cmd('tcpreplay -i h2-eth0 -x 4 --loop 0 --unique-ip /home/chamil/pcap/sm_dm.pcap > tcpreplay.out &')
    # h1.cmd('tcpreplay -i h1-eth0 -x 3 --loop 0 --unique-ip /mnt/CLAB/Chamil/merged/first24hour.cap > tcpreplay.out &')
    time.sleep(test_duration/3)

    # ATTCK
    # write_time("Start Attack")
    # h1.cmd('hping3 -d 32 -S -w 64 -p 21 --flood --rand-source 10.0.0.3 > hping3.out &')

    time.sleep(test_duration/3)

    # write_time("End Attack")
    # h1.cmd('killall hping3')

    #End Traffic
    time.sleep(test_duration/3)
    write_time("End Replaying traffic")
    h1.cmd('killall tcpreplay')

    ######Get Data
    write_time("Get Data")
    s1 = net.get('s1')

    for log_type in ['EXTERNAL', 'FLOWSTATS', 'FLOWTABLESTATS', 'NETFLOW', 'PORTSTATS']:
        fname = 'data/' + log_type + '/' + log_type + '.json'

        db.get_data(log_type, fname, list_of_sw= [str(int(s1.dpid))] )

    net.stop()
    Cleanup.cleanup()  ##Not sure post cleaing is a good idea
