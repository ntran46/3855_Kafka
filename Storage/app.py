import datetime
import os
import json
import connexion
import time
import logging.config
import yaml
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from brand import Brand
from item import Item

from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from sqlalchemy import and_


if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine(f"mysql+pymysql://"
                          f"{app_config['datastore']['user']}:"
                          f"{app_config['datastore']['password']}@"
                          f"{app_config['datastore']['hostname']}:"
                          f"{str(app_config['datastore']['port'])}/"
                          f"{app_config['datastore']['db']}")

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_item(start_timestamp, end_timestamp):
    """ Gets the item after a timestamp"""
    print(start_timestamp)
    start_timestamp = start_timestamp.replace("%20", " ")
    end_timestamp = end_timestamp.replace("%20", " ")
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    items = session.query(Item).filter(and_(Item.created_date >= start_timestamp_datetime,
                                            Item.created_date <= end_timestamp_datetime))
    results_list = []
    print(items)
    for item in items:
        results_list.append(item.to_dict())

    session.close()
    logger.info("Query for items after %s returns %d results" % (start_timestamp, len(results_list)))
    print(results_list)
    return results_list, 200


def get_brand(start_timestamp, end_timestamp):
    """ Gets the brand after a timestamp"""
    start_timestamp = start_timestamp.replace("%20", " ")
    end_timestamp = end_timestamp.replace("%20", " ")
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    brands = session.query(Brand).filter(and_(Brand.created_date >= start_timestamp_datetime,
                                              Brand.created_date <= end_timestamp_datetime))
    results_list = []
    print(brands)

    for brand in brands:
        results_list.append(brand.to_dict())

    session.close()
    logger.info("Query for brands after %s returns %d results" % (start_timestamp, len(results_list)))
    print(results_list)
    return results_list, 200


def process_messages():
    """ Process event messages """
    max_retry_count = app_config['events']['max_retry']
    sleep_time = app_config['events']['sleep']
    current_retry_count = 0
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)

    while current_retry_count < max_retry_count:
        logger.info(f"Connecting to Kafka {current_retry_count} of {max_retry_count}")
        try:
            topic = client.topics[str.encode(app_config['events']['topic'])]
            consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                                 reset_offset_on_start=False,
                                                 auto_offset_reset=OffsetType.LATEST)
            # consumer.stop()
            # consumer.start()
            logger.info("Connected! Processing messages")
            break
        except Exception as error:
            logger.error("Cannot connect to Kafka service")
            logger.error(error)
            time.sleep(sleep_time)
            current_retry_count += 1

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info(f"Message: {msg}")
        payload = msg['payload']

        session = DB_SESSION()

        if msg['type'] == "add_new_brand":
            new_brand = Brand(payload['brand_id'], payload['brand_name'],
                              payload['description'], payload['email_address'],
                              payload['phone_number'], payload['location'],
                              payload['last_update'])
            session.add(new_brand)
            logger.debug(f"Received event add_new_brand request with a unique id of {payload['brand_id']}")
        elif msg['type'] == "add_new_item":
            new_item = Item(payload['item_id'], payload['brand'],
                            payload['item_name'], payload['description'],
                            payload['price'], payload['quantities'],
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

