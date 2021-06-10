from flask import Flask
from flask_bootstrap import Bootstrap
from .database import mysql


def create_app():

    app = Flask(__name__)

    Bootstrap(app)

    app.config['SECRET_KEY'] = 'mysecret'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'Greenwich82'
    app.config['MYSQL_DB'] = 'dtbank'

    mysql.init_app(app)

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    return app
