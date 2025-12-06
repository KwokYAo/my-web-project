from application import app, db
from application.models import User, History

print("Connecting to database...")

with app.app_context():
    # This command forces the creation of all tables
    db.create_all()
    print("SUCCESS: Database tables (User, History) created!")