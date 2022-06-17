import os

basedir = os.path.abspath(os.path.dirname(__file__))

# basic configuration

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    AVATAR_UPLOAD_DIR = os.path.join(basedir, 'app/static/uploaded_AVATAR')
    AVATAR_DIR = os.path.join(basedir, 'app/static/images/avatar')
    BLOG_DIR = os.path.join(basedir, 'app/static/blog_PIC')
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_SUPPRESS_SEND = False
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = '535073436@qq.com'
    MAIL_PASSWORD = 'jixtaqgzowovbhdh'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flower Shop]'
    FLASKY_MAIL_SENDER = '535073436@qq.com'
    # FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_ADMIN = 'staff1@staff.com'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 一页商品数量
    FLASKY_POSTS_PER_PAGE = 9
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_LIKER_PER_PAGE = 50

    LANGUAGES = ['en', 'zh']
    BABEL_DEFAULT_LOCALE = 'en'

    @staticmethod
    def init_app(app):
        pass


# define some  specific  configuration
# you can choose a suit one

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
