from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

from gunicorn.config import User

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-this"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "sqlite:///calhacks.db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "login"

    from app import models
    from app.routes import register_routes

    register_routes(app)

    with app.app_context():
        db.create_all()

        from app.models import User
        organizer = User.query.filter_by(
            email="organizer@calhacks.test"
        ).first()

        if not organizer:
            organizer = User(
                email="organizer@calhacks.test",
                role="organizer"
            )
            organizer.set_password("organizer123")
            db.session.add(organizer)
            db.session.commit()

    return app