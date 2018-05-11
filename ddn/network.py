#@@---------------------------@@
#  Author: Chamil Jayasundara
#  Date: 1/16/17
#  Description:
#@@---------------------------@@

import ast
#test
from mininet.node import CPULimitedHost
from mininet.net import Mininet
from mininet.node import RemoteController, Controller
from mininet.link import Link, Intf, TCLink
from mininet.util import dumpNodeConnections, dumpNetConnections, quietRun, waitListening
from mininet.log import info, error, debug, output, warn
import requests
from requests.auth import HTTPBasicAuth
import subprocess
import re
import sys

##This will enable easy creation of SDN network using mining, by creating an appropriate config file

class ODL(RemoteController):
    def __init__(self, name, ip, ports, **kwargs):
        self.api_uname = 'admin'
        self.api_passwd = 'admin' #default username and password
        self.http_port = ports['http']
        super(ODL, self).__init__(name, ip=ip, port=ports['openflow'], **kwargs)
        self.__start_sflow_loggin('data/SFLOW/SFLOW.log')

    def set_api_uname_and_password(self, uname, passwd):
        #
        self.api_uname = uname
        self.api_passwd = passwd

    def __start_sflow_loggin(self, path):
        subprocess.call('killall -9 sflowtool', shell=True)
        with open(path, 'w') as f:
            subprocess.Popen('sflowtool', stdout=f)

    def __query_data(self, data_type, metric_name, start_time=0, end_time=0, node_id='', data_category='', record_key=''):
        url = 'http://' + self.ip + ':' + str(self.http_port) \
                   + '/tsdr/' + data_type + '/query'
        tsdrkey = "[NID" + node_id + "=][DC" + data_category + "=][MN=" + metric_name + "][RK=" + record_key + "]"
        parameters = {'tsdrkey':tsdrkey, 'from':str(start_time), 'until': str(end_time)}

        return requests.get(url, params=parameters,
                            auth=HTTPBasicAuth(self.api_uname, self.api_passwd))

    def get_data(self, metric, start_time, end_time, file_prefix="", **kwargs):
        ##This function get data from the controller API
        log_text = ""

        if metric == 'NETFLOW':
            data_type = 'logs'

        else:
            data_type = 'metrics'

        r = self.__query_data(data_type, metric,
                              start_time=start_time, end_time=end_time, **kwargs)

        step = end_time -  start_time

        while u'"recordCount": 1000' in str(r.text):
            step = step/2
            r = self.__query_data(data_type, metric,
                                  start_time=start_time, end_time=start_time + step, **kwargs)

        current_start_time = start_time
        current_end_time = start_time + step

        while current_end_time <= end_time:
            r = self.__query_data(data_type, metric,
                                  start_time=current_start_time, end_time=current_end_time, **kwargs)

            curr_text = r.text

            # if u'"recordCount": 1000' in str(curr_text):
            #     #curr_text =  self.get_data(metric, current_start_time, current_end_time)
            #     #print "IN here brooo"
            #     sys.exit("Dannam briyoooo")

            log_text += curr_text
            current_start_time = current_end_time
            current_end_time += step
        # filename = 'data/' + metric + '/' + metric + '_' + start_time + '_' + end_time + '.log'
        filename =  'data/' + metric + '/' + file_prefix + "_" + metric + '.log'
        with open(filename, 'w') as outfile:
            outfile.write(log_text)

        return r


class MyNetwork(Mininet):

    def __init__(self, config):
        self.config = config
        self.linksDict = {}

        super(MyNetwork, self).__init__(host=CPULimitedHost, controller=None, link=TCLink)
        self.controller = ODL(config['controller']['name'], config['controller']['ip'], config['controller']['ports'])
        self.addController(self.controller)

        # Add hosts and switches
        h = 1
        for host_name in config['hosts']:
            ##Important work only for less than 10 hosts need work
            host = self.addHost(host_name, ip='10.0.0.' + str(h) + '/24', mac='00:00:00:00:00:0' + str(h))
            # host = self.addHost(host_name)
            h = h + 1
            print host_name + " IP:" + host.params['ip'] + "  mac:" + host.params['mac']


        # Adding switches
        for switch in config['switches']:
            #Note that the DPID would be the order of switches added here starting from 1
            sw  = self.addSwitch(switch)
            print switch + " dpip: " + sw.dpid


        # Add links
        for connection in config['connections']:
            # net.addLink(net.getNodeByName(connection['link'][0]),net.getNodeByName(connection['link'][1]), **connection['linkparm'] )
            link = ast.literal_eval(connection['link'])
            nodes = self.getNodeByName(link[0], link[1])
            self.addLink(*nodes, **connection['linkparm'])
            # self.linksDict[(connection['link'][0], connection['link'][1])] = added_link
            # self.linksDict[(connection['link'][1], connection['link'][0])] = added_link
            # # self.linksDict[connection['link'][1] + connection['link'][0]] = added_link

    #
    def link_down(self, src, dst):
        self.configLinkStatus(src, dst, 'down')

    def link_up(self, src, dst):
        self.configLinkStatus(src, dst, 'up')

    def update_link_parameters(self, srcName, dstName, opt):
        src = self.nameToNode[srcName]
        dst = self.nameToNode[dstName]
        connections = src.connectionsTo(dst)
        connections[0][0].config(**opt)  # configure only one interface, is this right
                                         # This will apparantly change from src to dst

    def enable_netflow(self, switches, collector):
        cmd = 'ovs-vsctl -- --id=@nf create NetFlow target=\"' + collector + \
              ':2055\" active-timeout=10'

        for sw in switches:
            cmd = cmd + ' -- set Bridge ' + sw.name + ' netflow=@nf'

        quietRun(cmd)

    def enable_sflow(self, switches, collector, sampling, polling):
        cmd = 'ovs-vsctl -- --id=@sflow create sflow agent=eth0 target=' + collector \
              + ' sampling=' + str(sampling) + ' polling=' + str(polling) + ' --'

        for sw in switches:
            cmd += ' -- set bridge ' + sw.name + ' sflow=@sflow'

        quietRun(cmd)

    def print_link_info(self):
        println =  "The Link Connection Information\n ##################\n"
        for link in self.links:
            println += str(link) + '\n'

        print println

    def print_interface_id(self):
        println = "The matching between interface name and ifindex ##################\n"
        match_table = {}
        for intf in [str(sw.intfs[iface]) for sw in self.switches for iface in sw.intfs]:
            if intf is not 'lo':
                with open('/sys/devices/virtual/net/' + intf + '/ifindex') as f:
                    ifindex = f.read()

                match_table[str(intf)] = ifindex.rstrip()
                println += str(intf) + ':' + ifindex

        print println
        return match_table

        ##################### Overdide iperf method
    def iperf(self, hosts=None, l4Type='TCP', udpBw='10M', fmt=None,
              seconds=5, port=5001, sim_dual='False',  xtra_args = None):
        """Run iperf between two hosts.
           hosts: list of hosts; if None, uses first and last hosts
           l4Type: string, one of [ TCP, UDP ]
           udpBw: bandwidth target for UDP test
           fmt: iperf format argument if any
           seconds: iperf time to transmit
           port: iperf port
           returns: two-element array of [ server, client ] speeds
           note: send() is buffered, so client rate can be much higher than
           the actual transmission rate; on an unloaded system, server
           rate should be much closer to the actual receive rate"""
        hosts = hosts or [self.hosts[0], self.hosts[-1]]
        assert len(hosts) == 2
        client, server = hosts
        output('*** Iperf: testing', l4Type, 'bandwidth between',
               client, 'and', server, '\n')
        server.cmd('killall -9 iperf')
        iperfArgs = 'iperf -p %d ' % port
        bwArgs = ''
        if l4Type == 'UDP':
            iperfArgs += '-u '
            bwArgs = '-b ' + udpBw + ' '
        elif l4Type != 'TCP':
            raise Exception('Unexpected l4 type: %s' % l4Type)
        if fmt:
            iperfArgs += '-f %s ' % fmt
        server.sendCmd(iperfArgs + '-s')
        if l4Type == 'TCP':
            if not waitListening(client, server.IP(), port):
                raise Exception('Could not connect to iperf on port %d'
                                % port)

        client_cmd = iperfArgs + '-t %d -c ' % seconds + server.IP() + ' ' + bwArgs

        if xtra_args:
            for xtra_arg in xtra_args:
                client_cmd += xtra_arg + ' '

        cliout = client.cmd(client_cmd)
        print('Client output: %s\n' % cliout)

        servout = ''
        # We want the last *b/sec from the iperf server output
        # for TCP, there are two of them because of waitListening
        count = 2 if l4Type == 'TCP' else 1
        while len(re.findall('/sec', servout)) < count:
            servout += server.monitor(timeoutms=5000)
        server.sendInt()
        servout += server.waitOutput()

        print('Server output: %s\n' % servout)
        result = [self._parseIperf(servout), self._parseIperf(cliout)]
        if l4Type == 'UDP':
            result.insert(0, udpBw)
        output('*** Results: %s\n' % result)
        return result
