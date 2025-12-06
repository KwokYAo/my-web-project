from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize the Flask App
app = Flask(__name__)

# [CONFIG] Add your secret key and database URI here
app.config['SECRET_KEY'] = 'your_secret_key_here' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ames.db'

# Initialize Plugins
db = SQLAlchemy(app)

# [FIX START] Initialize Login Manager ------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Where to send users who aren't logged in
# [FIX END] ---------------------------------------------

from application import routes