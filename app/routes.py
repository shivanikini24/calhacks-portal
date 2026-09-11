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
    VolunteerApplication,
    Review
)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def register_routes(app):

    @app.route("/")
    def home():
        return render_template("index.html")


    # -------------------------
    # AUTHENTICATION
    # -------------------------

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

                if user.role == "organizer":
                    return redirect(url_for("organizer"))

                return redirect(url_for("dashboard"))

            flash("Invalid email or password.")

        return render_template("login.html")


    @app.route("/logout")
    @login_required
    def logout():

        logout_user()

        return redirect(url_for("home"))


    # -------------------------
    # APPLICANT DASHBOARD
    # -------------------------

    @app.route("/dashboard")
    @login_required
    def dashboard():

        if current_user.role == "organizer":
            return redirect(url_for("organizer"))

        return render_template(
            "dashboard.html",
            application=current_user.application
        )


    # -------------------------
    # APPLICATION
    # -------------------------

    @app.route("/application", methods=["GET", "POST"])
    @login_required
    def application():
        existing = current_user.application

        if existing and existing.status == "Submitted" and request.method == "POST":
            flash("Your application has already been submitted and cannot be edited.")
            return redirect(url_for("application"))
        if current_user.role == "organizer":
            return redirect(url_for("organizer"))


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

            action = request.form.get("action")

            if action == "submit":
                application.status = "Submitted"
                flash("Application submitted successfully!")

            else:
                application.status = "Draft"
                flash("Application draft saved.")

            db.session.commit()

            return redirect(url_for("dashboard"))

        return render_template(
            "application.html",
            application=existing
        )


    # -------------------------
    # ORGANIZER DASHBOARD
    # -------------------------

    @app.route("/organizer")
    @login_required
    def organizer():

        if current_user.role != "organizer":
            flash("Organizer access required.")
            return redirect(url_for("dashboard"))

        status_filter = request.args.get("status", "All")
        role_filter = request.args.get("role", "All")

        query = Application.query

        if status_filter != "All":
            query = query.filter_by(status=status_filter)

        if role_filter != "All":
            query = query.filter_by(role=role_filter)

        applications = query.order_by(
            Application.created_at.desc()
        ).all()

        all_applications = Application.query.all()

        stats = {
            "total": len(all_applications),
            "submitted": sum(
                a.status == "Submitted"
                for a in all_applications
            ),
            "accepted": sum(
                a.status == "Accepted"
                for a in all_applications
            ),
            "waitlisted": sum(
                a.status == "Waitlisted"
                for a in all_applications
            ),
            "rejected": sum(
                a.status == "Rejected"
                for a in all_applications
            )
        }

        return render_template(
            "organizer.html",
            applications=applications,
            stats=stats,
            status_filter=status_filter,
            role_filter=role_filter
        )
    # -------------------------
    # REVIEW APPLICATION
    # -------------------------

    @app.route("/organizer/application/<int:application_id>", methods=["GET", "POST"])
    @login_required
    def review_application(application_id):

        if current_user.role != "organizer":
            flash("Organizer access required.")
            return redirect(url_for("dashboard"))

        application = db.session.get(Application, application_id)

        if not application:
            flash("Application not found.")
            return redirect(url_for("organizer"))

        review = Review.query.filter_by(
            application_id=application.id,
            organizer_id=current_user.id
        ).first()

        if not review:
            review = Review(
                application_id=application.id,
                organizer_id=current_user.id
            )
            db.session.add(review)

        if request.method == "POST":

            review.technical_score = int(
                request.form["technical_score"]
            )

            review.creativity_score = int(
                request.form["creativity_score"]
            )

            review.communication_score = int(
                request.form["communication_score"]
            )

            review.comments = request.form["comments"]

            review.recommendation = request.form["recommendation"]

            application.status = request.form["status"]

            db.session.commit()

            flash("Review saved successfully.")

            return redirect(url_for(
                "review_application",
                application_id=application.id
            ))

        return render_template(
            "review.html",
            application=application,
            review=review
        )