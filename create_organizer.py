from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():

    organizer = User(
        email="organizer@calhacks.test",
        role="organizer"
    )

    organizer.set_password("organizer123")

    db.session.add(organizer)
    db.session.commit()

    print("Organizer created!")