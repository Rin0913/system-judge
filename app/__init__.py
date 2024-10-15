import logging
import sys
from flask import Flask
from sqlalchemy import create_engine

from services import AuthService
from repositories import ProblemRepository
from controllers import problem_bp, auth_bp

LOGGING_LEVEL = {'debug': logging.DEBUG, 'info': logging.INFO}

def initialize_app(config_name):
    app = Flask(__name__)

    app.config.from_object(f"config.{config_name.capitalize()}Config")
    app.runtime_environment = config_name

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
    app.logger.warning("Test MEsage")

    # Services Initialization
    auth_service = AuthService()
    auth_service.init_app(app, app.config.get('JWT_SECRET'), judge_logger)

    # Problem Repository Initialization
    connection_string = (
        f"mysql+pymysql://{app.config.get('MYSQL_USER')}:{app.config.get('MYSQL_PSWD')}"
        f"@{app.config.get('MYSQL_HOST')}/{app.config.get('MYSQL_DB')}"
    )
    sql_engine = create_engine(connection_string)
    problem_repository = ProblemRepository()
    problem_repository.init_app(app, sql_engine, judge_logger)

    # Registering Blueprints
    app.register_blueprint(problem_bp, url_prefix='/problems')
    app.register_blueprint(auth_bp, url_prefix='/')

    return app
