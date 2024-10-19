import logging
import sys

import redis
from flask import Flask
from flask_cors import CORS
import mongoengine as me
from redlock import Redlock

from services import AuthService, DockerService, LdapService, WireguardService
from repositories import ProblemRepository, UserRepository, SubmissionRepository
from controllers import problem_bp, user_bp, auth_bp
from .judge_system import *

LOGGING_LEVEL = {'debug': logging.DEBUG, 'info': logging.INFO}

def initialize_app(config_name):

    # App Initialization
    app = Flask("System Judge")
    app.config.from_object(f"config.{config_name.capitalize()}Config")
    app.runtime_environment = config_name
    if app.config.get('ALLOW_CORS'):
        CORS(app)

    # Logger Initialization
    judge_logger = logging.getLogger(__name__)
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    judge_logger.setLevel(LOGGING_LEVEL[app.config.get('LOGGING_LEVEL')])

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    judge_logger.addHandler(stream_handler)

    if app.config.get('LOG_PATH'):
        file_handler = logging.FileHandler(app.config.get('LOG_PATH'))
        file_handler.setFormatter(log_formatter)
        judge_logger.addHandler(file_handler)

    app.logger.handlers = judge_logger.handlers

    # Repositories Initialization
    mongo_connection = (
            f'mongodb://{app.config.get("DB_USER")}:'
            f'{app.config.get("DB_PASSWORD")}@{app.config.get("DB_HOST")}'
    )
    me.connect(db=app.config.get("DB_NAME"), host=mongo_connection)
    problem_repository = ProblemRepository()
    problem_repository.init_app(app, judge_logger)
    user_repository = UserRepository()
    user_repository.init_app(app, judge_logger)
    submission_repository = SubmissionRepository()
    submission_repository.init_app(app, judge_logger)

    # Services Initialization
    auth_service = AuthService()
    auth_service.init_app(app,
                          app.config.get('JWT_SECRET'),
                          user_repository,
                          judge_logger)
    docker_service = DockerService()
    docker_service.init_app(app, app.config, judge_logger)
    ldap_service = LdapService()
    ldap_service.init_app(app, app.config)
    wireguard_service = WireguardService()
    wireguard_service.init_app(app, app.config.get('WG_LISTEN_IP'), judge_logger)

    # Registering Blueprints
    app.register_blueprint(problem_bp, url_prefix='/problems')
    app.register_blueprint(user_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/')

    # Redis Initialization
    app.redis_dlm = Redlock([{"host": "localhost", "port": 6379, "db": 0}])

    # Network Initialization
    for wg_profile_id in user_repository.list_wg_id():
        wireguard_service.set_up(wg_profile_id)

    # Judge System Initialization
    initialize_judge(app.config,
                     problem_repository,
                     user_repository,
                     submission_repository,
                     judge_logger)

    return app
