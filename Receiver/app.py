import os

import logging
import logging.config
import connexion
import yaml
from connexion import NoContent
import json
import os.path
import requests

import datetime
from pykafka import KafkaClient

MAX_EVENTS = 12
EVENT_FILE = "event.json"

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def logging(body):
    """Log all successful requests to a text file"""
    if os.path.exists(EVENT_FILE):
        with open(EVENT_FILE, "r") as f:
            temp = f.read()
        history = json.loads(temp)
        if len(history) >= MAX_EVENTS:
            history.pop(0)
        history.append(body)
        with open(EVENT_FILE, "w") as f:
            f.write(json.dumps(history))
    else:
        with open(EVENT_FILE, "w") as f:
            f.write(json.dumps(body))


def add_new_item(body):
    """Send a request to add a new item into the Inventory List """

    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()

    msg = {"type": "add_new_item",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%H:%M:%S"),
           "payload": body}

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Received event add-new-item request with a unique id of item_id: {body['item_id']}")
    logger.info(f"Returned event from add-new-item response with ID:{body['item_id']} with status: 201")

    return NoContent, 201


def add_new_brand(body):
    """Send a request to add a new brand into the Inventory List"""

    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()

    msg = {"type": "add_new_brand",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%H:%M:%S"),
           "payload": body}

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Received event add_new_brand request with a unique id of brand_id: {body['brand_id']}")
    logger.info(f"Returned event from add_new_brand response with ID:{body['brand_id']} with status: 201")

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)
