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
    # SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:123@localhost:5432/practice_flask'


class EmailConfig:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'priyagorkha711@gmail.com'
    MAIL_PASSWORD = 'qlktjwwmrajmxuvp'
    MAIL_USE_SSL = True


config_dict = {"development": DevelopmentConfig, "testing": Testing, "email_config": EmailConfig}
