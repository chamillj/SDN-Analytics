#@@---------------------------@@
#  Author: Chamil Jayasundara
#  Date: 5/18/17
#  Description:
#@@---------------------------@@

from cassandra.cluster import Cluster
import requests
import json

class CassendraDB:

    def __init__(self):
        cluster = Cluster()
        self.session = cluster.connect('tsdr')

    def delete_content(self):
        self.session.execute('truncate metricval')
        self.session.execute('truncate metriclog')
        self.session.execute('truncate metricblob')


class ElastricsearchDB:

    def __init__(self, url="localhost"):
        self.url = "http://" + url + ":9200/"

    def delete_content(self):
        requests.delete(self.url + "tsdr")

    def create_snapshot(self):
        print "whatever"

    def get_data(self, param, file=None, list_of_sw = None):

        if param == 'NETFLOW':
            search_url = self.url + "tsdr/log/_search"

        else:
            search_url = self.url + "tsdr/metric/_search"

        optional_query = []

        if list_of_sw and param != 'NETFLOW' :
            for sw in list_of_sw:
                optional_query.append({"match": {"NodeID": sw}})

        else:
            optional_query.append({"match_all": {}})

        query = json.dumps(
            {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"TSDRDataCategory" : param}}
                        ],
                        # "should": optional_query
                        "should": optional_query,
                        "minimum_should_match": 1
                    }
                },
                # "_source": ["name", "bw", "hostname", "time", "to"],
                "size": 100,
                "sort": [
                    {"TimeStamp":{"order":"asc"}}
                ]
            })

        scroll = True

        response = requests.post(search_url + "?scroll=1m", data=query)
        results_dict = json.loads(response.text)
        scrollId = results_dict["_scroll_id"]

        results = []

        if results_dict['hits']['hits']:
            scroll = True
            for i in results_dict['hits']['hits']:
                results.append(results_dict['hits']['hits'][0]['_source'])


        while scroll:
            data = json.dumps(
                {
                    "scroll": "1m",
                    "scroll_id": scrollId
                }
            )
            response = requests.post(self.url+ "_search/scroll", data=data)
            results_dict = json.loads(response.text)
            if results_dict['hits']['hits']:
                scroll = True
                for i in results_dict['hits']['hits']:
                    results.append(results_dict['hits']['hits'][0]['_source'])
            else:
                scroll=False

        if file:
            with open(file, 'w') as outfile:
                json.dump(results, outfile, sort_keys=True, indent=4)

        return results


Database = ElastricsearchDB


if __name__ == '__main__':
    db = Database()
    # res =  db.delete_content()
    res = db.get_data("NETFLOW", list_of_sw=['1'])
    print("done")