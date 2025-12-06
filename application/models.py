from application import db, login_manager
from flask_login import UserMixin
from datetime import datetime

# [CRITICAL FIX] This function allows Flask-Login to load a user from the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User Table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # Link to History
    history = db.relationship('History', backref='author', lazy=True, cascade="all, delete-orphan")

# History Table
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    predicted_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Input Features (Saved so we can show them in history)
    overall_qual = db.Column(db.Integer, nullable=False)
    gr_liv_area = db.Column(db.Integer, nullable=False)
    garage_cars = db.Column(db.Integer, nullable=False)
    total_bsmt_sf = db.Column(db.Integer, nullable=False)
    year_built = db.Column(db.Integer, nullable=False)
    
    # The Result
    prediction = db.Column(db.Float, nullable=False)
    
    # Link back to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)