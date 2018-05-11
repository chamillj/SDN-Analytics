import json
from sflow import Trace

def write_file(dict):
    with open('file.json', 'a') as file:
        file.write(json.dumps(dict))  # use `json.loads` to do the reverse

if __name__ == '__main__':


    myTrace = Trace(callable=write_file)

    with open('../data/SFLOW/SFLOW2.log') as f:
        for line in f:
            myTrace.process(line)

    print "done"
