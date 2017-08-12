import time
import math
from google.cloud import datastore
import simplejson as json

# SMA explained:
# https://www.cryptocompare.com/exchanges/guides/how-to-trade-bitcoin-and-other-crypto-currencies-using-an-sma/

def calc_averages(symbol):

    # todo: get prices from datastore for <symbol> for last 2^11 minutes

    num_full_history_minutes = math.pow(2, 11)

    # client = datastore.Client()
    # query = client.query(kind='Channels', order=['-date'])
    # content = list(query.fetch(limit=math.pow(2,11)))[0]['content']
    # result = json.loads(content.replace("'", "\""))


    minute_prices = []

    assert len(minute_prices) % 15 == 0
    assert len(minute_prices) > 24 * 15

    unix_now = int(time.time())  # seconds
    averages = {}

    # for each period size
    for magnitude in range(1, 12):
        length_of_minutes = math.pow(2, magnitude)  # minutes

        some_time = (60 * length_of_minutes) + 40  # seconds
        some_timestamp_in_history = unix_now - some_time  # seconds

        # get all prices since some_timestamp_in_history
        # todo: filter prices priviously pulled from datastore
        prices = [1, 2, 3]

        average_price = float(sum(prices)) / len(prices)

        averages[magnitude] = average_price

    # todo: save averages to datastore
    # (unix_now, averages)  # save to datastore

    return


def get_sma(symbol, num_periods=12, period_magnitude=6):  # default = 12 x 64min intervals ~12 hrs
    unix_now = int(time.time())  # seconds

    minutes_in_period = math.pow(2, period_magnitude)
    # minutes_of_history = num_periods * minutes_in_period
    # seconds_of_history = (60 * minutes_of_history) + 40 # add 40 seconds buffer
    some_time = (60 * num_periods * minutes_in_period) + 40  # seconds

    # todo: get averages from datastore since <some_time>
    averages = [
        # (1416667766, {2:45, 4:43, 8:42, 16:41,
        #               32:42, 64:43, 128:45, 256:46,
        #               512:46, 1024:46, 2048:47]
        # ),
        # ...
    ]

    # for all averages, sum values for the appropriate minutes_in_period
    try:
        sma = sum([averages[1][minutes_in_period] for average in averages])
    except:
        # todo: exception for missing key in dict, (minutes_in_period not found for any average)
        # todo get previous SMA from datastore and repeat that one
        sma = 0

    # todo: save SMA in datastore
    # (unix_now, num_periods, period_magnitude, sma)  # save to datastore and/or cache

    return sma


def sma(client, datastore_entity, timestamp):

    content = datastore_entity['content']
    channel = datastore_entity['channel']
    result = json.loads(content.replace("'", "\""))

    # connection to datastore already provided
    # client = datastore.Client()

    for symbol_pair, price_data in result.items():

        if symbol_pair[0:4] == "BTC_":
            symbol = symbol_pair[4:]