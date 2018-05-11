#@@---------------------------@@
#  Author: Chamil Jayasundara
#  Date: 5/18/17
#  Description: import netwflow data
#@@---------------------------@@

import json

def parse_netflow(filename):
    with open(filename) as data_file:
        data = json.load(data_file)

    for record in data['logRecords']:
        record["entries"] = {}
        for key_val in [ entry.split("=") for entry in record['recordFullText'].split(",") ] :
            record["entries"][key_val[0]] = key_val[1]

        del record['recordFullText']

    return data['logRecords']


if __name__ == '__main__':
    netflow_data = parse_netflow('./NETFLOW.log')
    print netflow_data