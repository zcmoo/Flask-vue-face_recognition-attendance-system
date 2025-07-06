from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/attendace/*": {"origins": "http://localhost:5173"}})
app.config.from_object('config')
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)
from app.recognition.arcface import ExtractEmbeddings
extract_embeddings = ExtractEmbeddings()
try:
    from app.routes.login import login_routes
    from app.routes.admin_routes import admin_bp
    from app.routes.employee_routes import employee_bp
    from app.routes.attendace_routes import attendace_routes
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(attendace_routes, url_prefix='/attendace')
    app.register_blueprint(login_routes, url_prefix='/login')
except ImportError as e:
    print(f"Error importing blueprints: {e}")


