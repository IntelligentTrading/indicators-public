from google.cloud import datastore
import simplejson as json
import math



def price_average(client, datastore_entity, timestamp):

    content = datastore_entity['content']
    channel = datastore_entity['channel']
    result = json.loads(content.replace("'", "\""))

    for symbol_pair, price_data in result.items():

        if symbol_pair[0:4] == "BTC_":
            symbol = symbol_pair[4:]

            num_seconds_of_history = 60 * math.pow(2, 11)
            query = client.query(kind='Indicators')
            # query.add_filter('channel', '=', channel)
            query.add_filter('symbol', '=', symbol)
            query.add_filter('timestamp', '>=', (timestamp - num_seconds_of_history))
            query.order = ['timestamp']


def calc_averages_list(symbol_entity_list):

    pass


from google.cloud import datastore
client = datastore.Client()
query = client.query(kind='Indicators')
query.add_filter('ilk', '=', 'price')
symbol = "GNO"
query.add_filter('symbol', '=', symbol)
timestamp = 1502375580
import math
num_seconds_of_history = 60 * math.pow(2, 11)
query.add_filter('timestamp', '>=', (timestamp - num_seconds_of_history))
query.order = ['-timestamp']
entity_list = list(query.fetch())

