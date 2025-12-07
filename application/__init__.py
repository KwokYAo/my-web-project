from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os  
from application import routes
from application.models import User, History

# 1. Initialize the Flask App
app = Flask(__name__)

# [CONFIG]
app.config.from_pyfile('config.cfg')


uri = os.getenv("DATABASE_URL") 

if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///ames.db'

print("====================================")
if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
    print(" WARNING: Using SQLite (Data will be lost!)")
else:
    print(" SUCCESS: Using PostgreSQL (Data is safe!)")
print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
print("====================================")
# ========================================

db = SQLAlchemy(app)

# 3. Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 4. Force database creation on startup
with app.app_context():
    db.drop_all()

    db.create_all()
    print("-----------------------------------")
    print("Database tables created successfully!")
    print("-----------------------------------")