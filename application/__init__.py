from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os  # 1. 确保引入 os

# 1. Initialize the Flask App
app = Flask(__name__)

# [CONFIG]
app.config.from_pyfile('config.cfg')

# ================= 核心修改区 =================
# 必须在这里（在初始化 db 之前）决定用哪个数据库
uri = os.getenv("DATABASE_URI")

if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

# 如果 Render 给了地址就用 Render 的，否则用本地的 ames.db
app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///ames.db'
# ============================================

# 2. Initialize Plugins (这时候它就能读到正确的 URI 了)
db = SQLAlchemy(app)

# 3. Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# [CRITICAL FIX] 
from application import routes
from application.models import User, History

# 4. Force database creation on startup
with app.app_context():
    db.create_all()
    print("-----------------------------------")
    print("Database tables created successfully!")
    print("-----------------------------------")