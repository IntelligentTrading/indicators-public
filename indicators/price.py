from google.cloud import datastore
import simplejson as json


def store_prices(client, datastore_entity, timestamp):

    content = datastore_entity['content']
    channel = datastore_entity['channel']
    result = json.loads(content.replace("'", "\""))

    # connection to datastore already provided
    # client = datastore.Client()

    for symbol_pair, price_data in result.items():

        if symbol_pair[0:4] == "BTC_":
            symbol = symbol_pair[4:]

            # Poloniex Price Data Example
            # "BTC_PINK": {
            # "baseVolume": "22.07145048",
            # "high24hr": "0.00000448",
            # "highestBid": "0.00000411",
            # "id": 73,
            # "isFrozen": "0",
            # "last": "0.00000415",
            # "low24hr": "0.00000401",
            # "lowestAsk": "0.00000414",
            # "percentChange": "-0.06320541",
            # "quoteVolume": "5181417.61711973"
            # }

            entity = datastore.Entity(key=client.key('Indicators'))
            entity.update({
                'ilk': 'price',
                'symbol': symbol,
                'value': int(float(price_data['last'])*100000000), # satoshis
                'timestamp': timestamp,
                'channel': channel,
            })
            # print(entity)
            client.put(entity)

    print("saved prices for timestamp: %d" % timestamp)
    return True
