from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from app import db, login_manager
from app.models import (
    User,
    Application,
    HackerApplication,
    VolunteerApplication
)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def register_routes(app):

    @app.route("/")
    def home():
        return render_template("index.html")


    @app.route("/register", methods=["GET", "POST"])
    def register():

        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":

            email = request.form["email"].strip().lower()
            password = request.form["password"]
            role = request.form["role"]

            if role not in ["hacker", "volunteer"]:
                flash("Invalid account type.")
                return redirect(url_for("register"))

            existing_user = User.query.filter_by(email=email).first()

            if existing_user:
                flash("An account with that email already exists.")
                return redirect(url_for("register"))

            user = User(
                email=email,
                role=role
            )

            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            login_user(user)

            return redirect(url_for("application"))

        return render_template("register.html")


    @app.route("/login", methods=["GET", "POST"])
    def login():

        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":

            email = request.form["email"].strip().lower()
            password = request.form["password"]

            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):

                login_user(user)

                return redirect(url_for("dashboard"))

            flash("Invalid email or password.")

        return render_template("login.html")


    @app.route("/logout")
    @login_required
    def logout():

        logout_user()

        return redirect(url_for("home"))


    @app.route("/dashboard")
    @login_required
    def dashboard():

        return render_template(
            "dashboard.html",
            application=current_user.application
        )


    @app.route("/application", methods=["GET", "POST"])
    @login_required
    def application():

        existing = current_user.application

        if request.method == "POST":

            if existing:
                application = existing
            else:
                application = Application(
                    user_id=current_user.id,
                    role=current_user.role
                )

                db.session.add(application)
                db.session.flush()

            if current_user.role == "hacker":

                if application.hacker_application:
                    hacker = application.hacker_application
                else:
                    hacker = HackerApplication(
                        application_id=application.id
                    )
                    db.session.add(hacker)

                hacker.first_name = request.form["first_name"]
                hacker.last_name = request.form["last_name"]
                hacker.school = request.form["school"]
                hacker.major = request.form["major"]
                hacker.graduation_year = request.form["graduation_year"]
                hacker.github = request.form["github"]
                hacker.experience = request.form["experience"]
                hacker.why_cal_hacks = request.form["why_cal_hacks"]

            elif current_user.role == "volunteer":

                if application.volunteer_application:
                    volunteer = application.volunteer_application
                else:
                    volunteer = VolunteerApplication(
                        application_id=application.id
                    )
                    db.session.add(volunteer)

                volunteer.first_name = request.form["first_name"]
                volunteer.last_name = request.form["last_name"]
                volunteer.availability = request.form["availability"]
                volunteer.experience = request.form["experience"]
                volunteer.why_volunteer = request.form["why_volunteer"]

            application.status = "Submitted"

            db.session.commit()

            flash("Application submitted successfully!")

            return redirect(url_for("dashboard"))

        return render_template(
            "application.html",
            application=existing
        )