import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads' 
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'} 

db = SQLAlchemy(app)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(200), nullable=True)
    comments = db.relationship('Comment', backref='recipe', lazy=True)
    ratings = db.relationship('Rating', backref='recipe', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False) 

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False) 
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)  



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        title = request.form["title"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]
        file = request.files.get("photo")
        photo = None


        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
            photo = url_for('static', filename=f'uploads/{filename}')

        new_recipe = Recipe(title=title, ingredients=ingredients, instructions=instructions, photo=photo)
        db.session.add(new_recipe)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("add_recipe.html")

@app.route("/add_comment/<int:recipe_id>", methods=["POST"])
def add_comment(recipe_id):
    if request.method == "POST":
        comment_content = request.form["comment"]
        user_id = 1  
        new_comment = Comment(content=comment_content, recipe_id=recipe_id, user_id=user_id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('index'))
    
@app.route("/add_rating/<int:recipe_id>", methods=["POST"])
def add_rating(recipe_id):
    if request.method == "POST":
        rating = request.form["rating"]
        user_id = 1 
        new_rating = Rating(rating=rating, recipe_id=recipe_id, user_id=user_id)
        db.session.add(new_rating)
        db.session.commit()
        return redirect(url_for('index'))

@app.route("/", methods=["GET", "POST"])
def index():
    recipes = Recipe.query.all()
    for recipe in recipes:
        if recipe.ratings:
            total_rating = sum([rating.rating for rating in recipe.ratings])
            recipe.average_rating = total_rating / len(recipe.ratings)
        else:
            recipe.average_rating = None
    return render_template("index.html", recipes=recipes)

@app.route("/filter", methods=["GET", "POST"])
def filter_recipes():
    if request.method == "POST":
        ingredient = request.form["ingredient"]
        if ingredient:
           recipes = Recipe.query.filter(Recipe.ingredients == ingredient).all()
        else:
            recipes = Recipe.query.all()
    else:
        recipes = Recipe.query.all()

    return render_template("index.html", recipes=recipes)

if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
