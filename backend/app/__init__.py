import os
from os.path import abspath, dirname, join

from flask import Flask
from .extensions import db, socketio


def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)
    if config_object is None:
        app.config.from_object("config.Config")
    else:
        app.config.from_object(config_object)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    socketio.init_app(app)

    from .api.auth import bp as auth_bp
    from .api.items import bp as items_bp
    from .api.exchanges import bp as exchanges_bp
    from .api.messages import bp as messages_bp
    from .api.uploads import bp as uploads_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(items_bp, url_prefix="/api/items")
    app.register_blueprint(exchanges_bp, url_prefix="/api/exchanges")
    app.register_blueprint(messages_bp, url_prefix="/api/messages")
    app.register_blueprint(uploads_bp, url_prefix="/api/uploads")

    from . import events  # noqa: F401

    return app
