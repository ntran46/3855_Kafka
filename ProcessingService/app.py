import datetime
import json
import os.path
import connexion
# import logging
import logging.config

import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin
# from connexion import NoContent

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


# with open('app_conf.yml', 'r') as f:
#     app_config = yaml.safe_load(f.read())
#
# with open('log_conf.yml', 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)
#
# logger = logging.getLogger('basicLogger')

STATS = app_config["datastore"]["filename"]


def get_stats():
    """ Get the Inventory Statistics"""
    logger.info("Start Calculating statistics")
    if os.path.exists(STATS):
        with open(STATS, "r") as f:
            stats_data = f.read()
    else:
        logger.error("Statistic file does not exist")
        return "Statistics do not exist", 404

    logger.debug(f"Statistic data: {stats_data}")
    logger.info("Calculating statistics Ended")
    return json.loads(stats_data), 200


def populate_stats():
    """ Periodically update stats"""
    logger.info("Start Periodic Processing")
    current_datetime = str(datetime.datetime.now())

    temp = []

    stats = {'num_items_added': 0,
             'num_brands_added': 0,
             'max_items_quantity': 0,
             'min_items_quantity': 0,
             'last_updated': current_datetime}

    if os.path.exists(STATS):
        with open(STATS, "r") as f:
            temp1 = f.read()
            if len(temp1) > 0:
                stats = json.loads(temp1)

    r_item = requests.get(f"{app_config['eventstore']['url']}/get_item?"
                          f"start_timestamp={stats['last_updated']}&end_timestamp={current_datetime}")
    r_brand = requests.get(f"{app_config['eventstore']['url']}/get_brand?"
                           f"start_timestamp={stats['last_updated']}&end_timestamp={current_datetime}")

    temp.append(r_brand.json())
    temp.append(r_item.json())

    if len(temp[1]) != 0:
        stats['num_items_added'] = len(temp[1])
        stats['max_items_quantity'] = max([a_dict['quantities'] for a_dict in temp[1]])
        stats['min_items_quantity'] = min([a_dict['quantities'] for a_dict in temp[1]])
    if len(temp[0]) != 0:
        stats['num_brands_added'] = len(temp[0])

    stats['last_updated'] = str(datetime.datetime.now())

    with open(STATS, "w") as f:
        f.write(json.dumps(stats))

    if r_item.status_code != 200 or r_brand.status_code != 200:
        logger.error("Request failed")
    else:
        logger.info(f"Total event: item event - {len(r_item.json())}, brand-event - {len(r_brand.json())}")
        logger.info('Periodic Processing Ended')


def init_scheduler():
    """ """
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
# CORS(app.app)
# app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path="/processing", strict_validation=True, validate_responses=True)

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS']='Content-Type'

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)

