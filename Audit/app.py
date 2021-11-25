import logging.config
import connexion
import yaml

import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

from flask_cors import CORS, cross_origin

import os

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

# with open("app_conf.yml", 'r') as f:
#     app_config = yaml.safe_load(f.read())
#
# with open('log_conf.yml', 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

# logger.info("connecting to DB. Hostname: %s, Port: %d" % (app_config["datastore"]["hostname"],
#                                                           app_config["datastore"]["port"]))


def get_brand(index):
    """ Get item from an index in History"""

    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info(f"Retrieving the item at index {index}")

    try:
        for msg in consumer:
            print(f"Offset: {msg.offset}, Message: {msg.value} \n")
            offset = msg.offset
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if offset == int(index) and msg['type'] == 'add_new_brand':
                print(f"Message found: {msg}")
                return msg, 201
        raise ValueError
    except ValueError:
        logger.error("No more messages found")
        logger.error(f"Could not find the event at index {index}")
        return {"message": "Not Found"}, 404


def get_item(index):
    """ Get item from an index in History"""

    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)

    logger.info(f"Retrieving the item at index {index}")

    try:
        for msg in consumer:
            print(f"Offset: {msg.offset}, Message: {msg.value} \n")
            offset = msg.offset
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if offset == int(index) and msg['type'] == 'add_new_item':
                print(f"Message found: {msg}")
                return msg, 201
        raise ValueError
    except ValueError:
        logger.error("No more messages found")
        logger.error(f"Could not find the event at index {index}")
        return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
# CORS(app.app)
# app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path="/audit_log", strict_validation=True, validate_responses=True)

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS']='Content-Type'

if __name__ == "__main__":
    app.run(port=8070)
