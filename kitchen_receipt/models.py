from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(200), nullable=True)
