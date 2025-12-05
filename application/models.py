from application import db
from datetime import datetime

# 1. The User Table (For Login/Register)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False) 

    def __repr__(self):
        return f'<User {self.username}>'

# 2. The History Table (For Predictions)
class Entry(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    
    # The 5 Prediction Parameters
    overall_qual = db.Column(db.Integer, nullable=False)
    gr_liv_area = db.Column(db.Integer, nullable=False)
    garage_cars = db.Column(db.Integer, nullable=False)
    total_bsmt_sf = db.Column(db.Integer, nullable=False)
    year_built = db.Column(db.Integer, nullable=False)
    
    # The Result
    prediction = db.Column(db.Float, nullable=False)
    predicted_on = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f'<Entry {self.id}: {self.prediction}>'