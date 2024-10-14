from flask import Flask
from sqlalchemy import create_engine
from repositories import ProblemRepository
from controllers import problem_bp

def initialize_app(config_name):
    app = Flask(__name__)

    app.config.from_object(f'config.{config_name.capitalize()}Config')

    connection_string = (
        f"mysql+pymysql://{app.config.get('MYSQL_USER')}:{app.config.get('MYSQL_PSWD')}"
        f"@{app.config.get('MYSQL_HOST')}/{app.config.get('MYSQL_DB')}"
    )
    sql_engine = create_engine(connection_string)

    problem_repository = ProblemRepository()
    problem_repository.init_app(app, sql_engine)

    app.register_blueprint(problem_bp)

    return app
