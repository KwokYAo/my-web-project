# application/__init__.py
from flask import Flask
import pickle
from flask_sqlalchemy import SQLAlchemy

# run the file routes.py

db = SQLAlchemy()

# create the Flask app
app = Flask(__name__)

# load configuration from config.cfg
app.config.from_pyfile('config.cfg')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///housing.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# new method for SQLAlchemy version 3 onwards
with app.app_context():
    db.init_app(app)
    from .models import Entry
    db.create_all()
    db.session.commit()
    print('Created Database!')


from application import routes, models