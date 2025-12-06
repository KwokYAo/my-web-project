from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 1. Initialize the Flask App
app = Flask(__name__)

# [CONFIG]
app.config.from_pyfile('config.cfg')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ames.db'


# 2. Initialize Plugins
db = SQLAlchemy(app)

# 3. Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# [CRITICAL FIX] 
# Routes and Models MUST be imported AFTER 'app' and 'db' are created.
# This prevents the "Circular Import" error.
from application import routes
from application.models import User, History

# 4. Force database creation on startup
with app.app_context():
    db.create_all()
    print("-----------------------------------")
    print("Database tables created successfully!")
    print("-----------------------------------")