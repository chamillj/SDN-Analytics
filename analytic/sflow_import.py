
from sflow import Trace
from collections import defaultdict
import json
import numpy as np
import pickle
import csv


#####Script
# if the script is run directly (sudo custom/optical.py):



    # myTrace = myTrace.trace_data
    #
    # writer_CNT=csv.writer(open('sflow_CNT.csv','wb'))
    # writer_CNT.writerow(['TYPE', 'unixSecondsUTC', 'ifName', 'ifInOctets', 'ifOutOctets'])
    #
    # writer_FLOW=csv.writer(open('sflow_FLOW.csv','wb'))
    # writer_FLOW.writerow(['TYPE', 'unixSecondsUTC', 'inputIF', 'outputIF', 'Protocol', 'dstIP', 'srcIP', 'srcPort', 'dstPort', 'IPSize'])
    #
    # for d in myTrace:
    #     datagram = myTrace[d]
    #     for fs in datagram['flowSamples']:
    #         flow = datagram['flowSamples'][fs]
    #
    #         if flow['sampleType'] == 'COUNTERSSAMPLE':
    #             type = 'CNTR'
    #             writer_CNT.writerow(['CNTR', datagram['unixSecondsUTC'], flow['ifName'], flow['ifInOctets'], flow['ifOutOctets']])
    #
    #         elif flow['sampleType'] == 'FLOWSAMPLE':
    #
    #             protocol = 'UNKNOWN'
    #             srcPort = 0
    #             dstPort = 0
    #
    #             if flow['TCPDstPort'] and flow['TCPSrcPort']:
    #                 protocol = 'TCP'
    #                 srcPort = flow['TCPSrcPort']
    #                 dstPort = flow['TCPDstPort']
    #
    #             elif flow['UDPDstPort'] and flow['UDPSrcPort']:
    #                 protocol = 'UDP'
    #                 srcPort = flow['UDPSrcPort']
    #                 dstPort = flow['UDPDstPort']
    #
    #             elif flow['ICMPType']:
    #                 protocol = 'ICMP'
    #
    #             elif flow['dstMAC'] == 'ffffffffffff':
    #                 protocol = 'L2 Broadcast'
    #
    #             writer_FLOW.writerow(['FLOW', datagram['unixSecondsUTC'], flow['inputPort'], flow['outputPort'], protocol, flow['dstIP'], flow['srcIP'], srcPort, dstPort, flow['IPSize']])


class WriteCSV:

    def __init__(self):
        self.writer_CNT = csv.writer(open('sflow_CNT.csv', 'wb'))
        self.writer_CNT.writerow(['TYPE', 'unixSecondsUTC', 'ifName', 'ifInOctets', 'ifOutOctets'])

        self.writer_FLOW = csv.writer(open('sflow_FLOW.csv', 'wb'))
        self.writer_FLOW.writerow(
            ['TYPE', 'unixSecondsUTC', 'inputIF', 'outputIF', 'Protocol', 'dstIP', 'srcIP', 'srcPort', 'dstPort',
             'IPSize'])


    def __call__(self, datagram):

        for fs in datagram['flowSamples']:
            flow = datagram['flowSamples'][fs]

            if flow['sampleType'] == 'COUNTERSSAMPLE':
                type = 'CNTR'
                self.writer_CNT.writerow(
                    ['CNTR', datagram['unixSecondsUTC'], flow['ifName'], flow['ifInOctets'], flow['ifOutOctets']])

            elif flow['sampleType'] == 'FLOWSAMPLE':

                protocol = 'UNKNOWN'
                srcPort = 0
                dstPort = 0

                if flow['TCPDstPort'] and flow['TCPSrcPort']:
                    protocol = 'TCP'
                    srcPort = flow['TCPSrcPort']
                    dstPort = flow['TCPDstPort']

                elif flow['UDPDstPort'] and flow['UDPSrcPort']:
                    protocol = 'UDP'
                    srcPort = flow['UDPSrcPort']
                    dstPort = flow['UDPDstPort']

                elif flow['ICMPType']:
                    protocol = 'ICMP'

                elif flow['dstMAC'] == 'ffffffffffff':
                    protocol = 'L2 Broadcast'

                self.writer_FLOW.writerow(
                    ['FLOW', datagram['unixSecondsUTC'], flow['inputPort'], flow['outputPort'], protocol, flow['dstIP'],
                     flow['srcIP'], srcPort, dstPort, flow['IPSize']])

    # out = defaultdict(list)
    #
    # for datagram in myTrace:
    #     flowSamples = myTrace[datagram]['flowSamples']
    #
    #     for fs in flowSamples:
    #         flowSample = flowSamples[fs]
    #
    #         if flowSample['sampleType'] == "COUNTERSSAMPLE":
    #             entry = [int(myTrace[datagram]['unixSecondsUTC']), int(flowSample['ifInOctets']), int(flowSample['ifOutOctets'])]
    #             out[flowSample['ifName']].append(entry)
    #
    #
    # final_result = defaultdict(dict)
    #
    # for iface in [ifc for ifc in out if ifc != 0 and "-" in ifc]:
    #
    #     diff = np.diff(np.array(out[iface]), axis=0)
    #
    #     final_result[iface]['in']  = diff[:, 1] * 8 /(diff[:,0] * 1000000)
    #     final_result[iface]['out'] = diff[:, 2] * 8 /(diff[:,0] * 1000000)
    #
    #     print "In Interface" + str(iface)
    #     print(diff[:, 1] * 8 /(diff[:,0] * 1000000))
    #     print "Out Interface" + str(iface)
    #     print(diff[:, 2] * 8 /(diff[:,0] * 1000000))
    #     print "\n\n\n"
    #
    #
    # # data_file = open('data.pkl', 'wb')
    # # pickle.dump(final_result, data_file)
    # # data_file.close()


if __name__ == '__main__':

    #####IMPORT DATA TO DICT

    myTrace = Trace(callable=WriteCSV())

    with open('/home/chamil/myTests/DDOS/6hrs/SFLOW/SFLOW.log') as f:
        for line in f:
            myTrace.process(line)

    print "done"