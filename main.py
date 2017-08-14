""" Intelligent Trading Indicators App """
import os
from logging import basicConfig, INFO
from google.cloud import datastore
from google.cloud import pubsub
from indicators import price, price_average, sma, ema


basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=INFO)


# Tier 1 indicators have no dependencies
# They can run directly over the raw data from data sources
tier_1_indicators = [
    price.price,
]

# Tier 2 indicators have one or more dependencies on Tier 1 indicaotrs
# They should run after all Tier 1 indicators have completed processing
tier_2_indicators = [
    price_average.price_average
]

# Tier 3 indicators have one or more dependencies on Tier 2 indicaotrs
# They should run after all Tier 1 indicators have completed processing
tier_3_indicators = [
    # sma.sma,
    # ema.ema,
]


def refresh_indicator(indicator_function):
    client = datastore.Client()
    query = client.query(kind='Channels')
    # query.add_filter('channel', '=', channel)
    query.order = ['timestamp']
    datastore_entities = list(query.fetch())

    for datastore_entity in datastore_entities:
        timestamp = datastore_entity['timestamp']
        indicator_function(client, datastore_entity, timestamp)


def update_indicators(indicator_list, channel="Poloniex", refresh=False):

    # query database for latest price data
    client = datastore.Client()
    query = client.query(kind='Channels')
    # query.add_filter('channel', '=', channel)
    query.order = ['-timestamp']
    datastore_entities = list(query.fetch(limit=1))

    for datastore_entity in datastore_entities:
        timestamp = datastore_entity['timestamp']

    no_exceptions = True

    if refresh:
        # refresh all indicator data
        for indicator_function in indicator_list:
            refresh_indicator(indicator_function)

    else:
        # send to all indicator processors
        for indicator_function in indicator_list:
            try:
                indicator_function(client, datastore_entity, timestamp)
            except Exception as e:
                print(str(e))
                no_exceptions = False

    return no_exceptions

def main():
    """ Main """

    # todo: subscribe to new Poloniex datastore entities

    try:
        from google.cloud import pubsub
        client = pubsub.Client()
        topic = client.topic('indicators-topic')
        assert topic.exists()
        subscription = client.subscription('public-indicators-subscription')
        assert subscription.exists()
        print("subscription activated")

        # while True:
        while True:
            print("pulling messages")
            pulled = subscription.pull(max_messages=2)
            for ack_id, message in pulled:

                try:
                    message = message.data.decode()
                    print("received message: " + message)

                    refresh = ("new" not in message and "refresh" in message)

                    if "Poloniex" in message:
                        channel = "Poloniex"
                    elif "Bittrex" in message:
                        channel = "Bittrex"
                    else:
                        channel = None

                    success = True

                    if channel:
                        if "data" in message:
                            for indicator_tier_list in [
                                tier_1_indicators,
                                tier_2_indicators,
                                tier_3_indicators,
                            ]:
                                if success: #continue if previous tier was successful
                                    success = update_indicators(indicator_tier_list,
                                                                channel=channel,
                                                                refresh=refresh)

                except AttributeError as e:
                    print(str(e))
                    subscription.acknowledge([ack_id])

                except Exception as e:
                    print(str(e))

                else:
                    subscription.acknowledge([ack_id])

    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main()
