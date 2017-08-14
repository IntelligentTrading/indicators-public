""" Intelligent Trading Indicators App """
import os
from logging import basicConfig, INFO
from google.cloud import datastore
from google.cloud import pubsub
from indicators import price, sma, ema


basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=INFO)


# Tier 1 indicators have no dependencies
# They can run directly over the raw data from data sources
tier_1_indicators = [
    price.price,
]

# Tier 2 indicators have one or more dependaencies on Tier 1 indicaotrs
# They should run after all Tier 1 indicators have completed processing
tier_2_indicators = [
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
    datastore_entity = list(query.fetch(limit=1))[0]

    timestamp = datastore_entity['timestamp']

    if refresh:
        # refresh all indicator data
        for indicator_function in indicator_list:
            refresh_indicator(indicator_function)

    else:
        # send to all indicator processors
        for indicator_function in indicator_list:
            indicator_function(client, datastore_entity, timestamp)


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

        # while True:
        while True:
            pulled = subscription.pull(max_messages=2)
            for ack_id, message in pulled:

                try:
                    message = message.data.decode()
                    print(message)

                    refresh = ("new" not in message and "refresh" in message)

                    if "Poloniex" in message:
                        if "data" in message:
                            update_indicators(tier_1_indicators,
                                              channel="Poloniex",
                                              refresh=refresh)
                            update_indicators(tier_2_indicators,
                                              channel="Poloniex",
                                              refresh=refresh)

                    # elif "Bittrex" in message:
                    #     if "data" in message:
                    #         update_indicators(tier_1_indicators,
                    #                           channel="Bittrex",
                    #                           refresh=refresh)
                    #         update_indicators(tier_2_indicators,
                    #                           channel="Bittrex",
                    #                           refresh=refresh)

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
