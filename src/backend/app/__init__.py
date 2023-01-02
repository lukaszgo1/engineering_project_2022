from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
with app.app_context():
    db.Model.metadata.reflect(bind=db.engine)
from app import routes