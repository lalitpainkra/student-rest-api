
import os
import logging

from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv

from app.models import db

load_dotenv()

migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.get("/healthcheck")
    def healthcheck():
        return {"status": "healthy"}, 200

    return app

