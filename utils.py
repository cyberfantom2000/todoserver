import os
import json
import argparse
import logging.config
from typing import Iterable
from sqlmodel import SQLModel


def is_models_collection(model):
    return not isinstance(model, SQLModel) and isinstance(model, Iterable)


def create_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9999, help='Listening port')
    parser.add_argument('--host', default='0.0.0.0', help='Binding address')
    return parser


LOG_FOLDER = 'log'
LOG_CONFIG = 'logger.json'


def get_logger(name: str, template: str = 'default'):
    if not os.path.exists(LOG_FOLDER):
        os.mkdir(LOG_FOLDER)
    with open(LOG_CONFIG, 'r') as file:
        config = json.load(file)
        config['loggers'][name] = config['loggers'][template]
    logging.config.dictConfig(config)
    return logging.getLogger(name)
