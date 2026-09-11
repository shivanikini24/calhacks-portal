from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)

    application = db.relationship(
        "Application",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    role = db.Column(db.String(20), nullable=False)

    status = db.Column(
        db.String(20),
        default="Draft",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    hacker_application = db.relationship(
        "HackerApplication",
        backref="application",
        uselist=False,
        cascade="all, delete-orphan"
    )

    volunteer_application = db.relationship(
        "VolunteerApplication",
        backref="application",
        uselist=False,
        cascade="all, delete-orphan"
    )

    reviews = db.relationship(
        "Review",
        backref="application",
        cascade="all, delete-orphan"
    )


class HackerApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("application.id"),
        nullable=False
    )

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    school = db.Column(db.String(150), nullable=False)
    major = db.Column(db.String(150))

    graduation_year = db.Column(db.Integer)

    github = db.Column(db.String(255))
    experience = db.Column(db.Text)
    why_cal_hacks = db.Column(db.Text)


class VolunteerApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("application.id"),
        nullable=False
    )

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    availability = db.Column(db.String(255))
    experience = db.Column(db.Text)
    why_volunteer = db.Column(db.Text)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("application.id"),
        nullable=False
    )

    organizer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    technical_score = db.Column(db.Integer)
    creativity_score = db.Column(db.Integer)
    communication_score = db.Column(db.Integer)

    comments = db.Column(db.Text)

    recommendation = db.Column(db.String(30))