from google.cloud import datastore
import simplejson as json
import math


def price_average(client, datastore_entity, timestamp):

    content = datastore_entity['content']
    channel = datastore_entity['channel']

    # check which symbols have new prices
    symbol_query = client.query(kind='Indicators')
    symbol_query.add_filter('timestamp', '>=', timestamp)
    symbol_query.order = ['timestamp']
    # symbol_query.projection = ['channel', 'symbol']
    symbol_entity_list = list(symbol_query.fetch())

    #get history for calculating all averages
    num_seconds_of_history = 60 * math.pow(2, 11)
    price_query = client.query(kind='Indicators')
    price_query.add_filter('timestamp', '>=', (timestamp - num_seconds_of_history))
    # price_query.projection = ['symbol', 'value', 'timestamp']
    price_query.order = ['timestamp']
    price_entity_list = list(price_query.fetch())

    for symbol_entity in symbol_entity_list:
        if symbol_entity['timestamp'] == timestamp:

            averages = calc_averages_list(symbol_entity['symbol'],
                                          price_entity_list,
                                          timestamp)
            print(averages)

            averages_entity = datastore.Entity(key=client.key('Indicators'))
            averages_entity.update({
                'ilk': 'average',
                'symbol': symbol_entity['symbol'],
                'value': str(averages),
                'timestamp': timestamp,
                'channel': symbol_entity['channel'],
            })
            client.put(averages_entity)


def calc_averages_list(symbol, price_entity_list, now_timestamp):

    #convert price_entity_list to list of integers

    # create dict for averages
    exponents = range(2,12)
    minute_sizes = [math.pow(2,exponent) for exponent in exponents]
    averages = {minute_size: (0,0) for minute_size in minute_sizes}

    # for each data from the database
    for price_entity in price_entity_list:

        # check that matches the correct symbol
        if price_entity['symbol'] == symbol:

            # for each period size to calculate
            for minute_size in minute_sizes:

                # if timestamp is within the period
                if (now_timestamp - price_entity['timestamp']) <= (minute_size * 60):

                    # update average by adding new price
                    average_price = (
                        (averages[minute_size][1] * averages[minute_size][0]) +
                            price_entity['value']
                        ) / (
                            averages[minute_size][1] + 1
                        )

                    averages[minute_size] = (int(average_price),
                                             averages[minute_size][1] + 1)

    return [
        (minute_size, int(average_price))
        for (minute_size, (average_price, weight)) in averages.items()
    ]
