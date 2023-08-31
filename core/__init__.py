from flask import Flask
from flask_sqlalchemy import SQLAlchemy # orm mapping
from flask_migrate import Migrate  # libray alympic
from .config import config_dict

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_mode):
    instance = Flask(__name__)
    instance.config.from_object(config_dict[config_mode])
    instance.config.from_object(config_dict['email_config'])
    instance.config["RESTX_MASK_SWAGGER"] = False
    db.init_app(instance)# binding done
    migrate.init_app(instance, db)
    return instance
