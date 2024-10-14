import logging
import sys
from flask import Flask
from sqlalchemy import create_engine

from repositories import ProblemRepository
from controllers import problem_bp

LOGGING_LEVEL = {'debug': logging.DEBUG, 'info': logging.INFO}

def initialize_app(config_name):
    app = Flask(__name__)

    app.config.from_object(f"config.{config_name.capitalize()}Config")

    connection_string = (
        f"mysql+pymysql://{app.config.get('MYSQL_USER')}:{app.config.get('MYSQL_PSWD')}"
        f"@{app.config.get('MYSQL_HOST')}/{app.config.get('MYSQL_DB')}"
    )
    sql_engine = create_engine(connection_string)

    logger = logging.getLogger(__name__)
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(LOGGING_LEVEL[app.config.get('LOGGING_LEVEL')])

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    if app.config.get('LOG_PATH'):
        file_handler = logging.FileHandler(app.config.get('LOG_PATH'))
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)

    app.logger.handlers = logger.handlers
    app.logger.warning("Test MEsage")

    problem_repository = ProblemRepository()
    problem_repository.init_app(app, sql_engine, logger)

    app.register_blueprint(problem_bp)

    return app
