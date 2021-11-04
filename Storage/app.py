import datetime

import connexion
import logging
import logging.config
import yaml
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Storage.base import Base
from Storage.brand import Brand
from Storage.item import Item

import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f"mysql://"
                          f"{app_config['datastore']['user']}:"
                          f"{app_config['datastore']['password']}@"
                          f"{app_config['datastore']['hostname']}:"
                          f"{str(app_config['datastore']['port'])}/"
                          f"{app_config['datastore']['db']}")

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_item(timestamp):
    """ Gets the item after a timestamp"""
    print(timestamp)
    timestamp = timestamp.replace("%20", " ")
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

    items = session.query(Item).filter(Item.created_date >= timestamp_datetime)
    results_list =[]

    for item in items:
        results_list.append(item.to_dict())

    session.close()
    logger.info("Query for items after %s returns %d results" % (timestamp, len(results_list)))
    print(results_list)
    return results_list, 200


def get_brand(timestamp):
    """ Gets the brand after a timestamp"""
    timestamp = timestamp.replace("%20", " ")
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

    brands = session.query(Brand).filter(Brand.created_date >= timestamp_datetime)
    results_list = []

    for brand in brands:
        results_list.append(brand.to_dict())

    session.close()
    logger.info("Query for brands after %s returns %d results" % (timestamp, len(results_list)))
    print(results_list)
    return results_list, 200


def process_messages():
    """ Process event messages """
    session = DB_SESSION()

    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group='event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info(f"Message: {msg}")

        payload = msg['payload']

        if msg['type'] == "add_new_brand":
            new_brand = Brand(payload['brand_id'],
                              payload['brand_name'],
                              payload['description'],
                              payload['email_address'],
                              payload['phone_number'],
                              payload['location'],
                              payload['last_update'])
            session.add(new_brand)
            logger.debug(f"Received event add_new_brand request with a unique id of {payload['brand_id']}")
        elif msg['type'] == "add_new_item":
            new_item = Item(payload['item_id'],
                            payload['brand'],
                            payload['item_name'],
                            payload['description'],
                            payload['price'],
                            payload['quantities'],
                            payload['last_update'])
            session.add(new_item)
            logger.debug(f"Received event add_new_item request with a unique id of {payload['item_id']}")

        session.commit()
        session.close()
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    tl = Thread(target=process_messages)
    tl.setDaemon(True)
    tl.start()
    app.run(port=8090)
