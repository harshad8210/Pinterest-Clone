from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from pinterest.config import Config
from flask_migrate import Migrate
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login_page'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    application = Flask(__name__)
    application.config.from_object(Config)

    db.init_app(application)
    migrate.init_app(application, db)
    bcrypt.init_app(application)
    login_manager.init_app(application)
    mail.init_app(application)

    from pinterest.users.routes import users
    from pinterest.pins.routes import pins
    from pinterest.main.routes import main
    from pinterest.admin.routes import admin

    application.register_blueprint(users)
    application.register_blueprint(pins)
    application.register_blueprint(main)
    application.register_blueprint(admin)

    return application
