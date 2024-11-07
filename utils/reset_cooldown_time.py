import argparse
import logging

import redis
import mongoengine as me

from app.repositories import UserRepository
from config import Config as config

parser = argparse.ArgumentParser(description="System Judge - cooldown time reset tool")

parser.add_argument('-u', '--username', help="The username you want to reset.")
parser.add_argument('-p', '--problem', help="The problem you want to reset.")

args = parser.parse_args()

mongo_connection = (
    f'mongodb://{config.DB_USER}:'
    f'{config.DB_PASSWORD}@{config.DB_HOST}'
)
me.connect(config.DB_NAME, host=mongo_connection)

user_repository = UserRepository(logging)
redis = redis.StrictRedis(host=config.REDIS_HOST,
                          port=config.REDIS_PORT,
                          db=0)

uid = user_repository.query(args.username)['_id']
problem = args.problem
redis.set(f"cooldown_p{problem}_u{uid}", 1, ex=1)
