from settings import settings


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = settings.DB_URI


class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = settings.TEST_URI


class EmailConfig:
    MAIL_SERVER = settings.MAIL_SERVER
    MAIL_PORT = settings.MAIL_PORT
    MAIL_USE_TLS = False
    MAIL_USERNAME = settings.MAIL_USERNAME
    MAIL_PASSWORD = settings.MAIL_PASSWORD
    MAIL_USE_SSL = True


config_dict = {"development": DevelopmentConfig, "testing": Testing, "email_config": EmailConfig}
