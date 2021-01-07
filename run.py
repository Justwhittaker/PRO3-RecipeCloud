import os
import datetime
import favicon
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from flask_paginate import Pagination, get_page_parameter
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# Home page - Search bar and all recipes shorthand discription
@app.route('/')
def index():
    # recipes on the page to show 3
    per_page = 3
    page = request.args.get(get_page_parameter(), type=int, default=1)
    recipes = mongo.db.recipes.find().sort("timestamp", -1)
    # pagination for users to flip through different recipes
    pagination = Pagination(page=page, total=recipes.count(),
                            per_page=per_page,
                            search=False, record_name='recipes',
                            css_framework='bootstrap4', alignment='center')
    recipe_page = recipes.skip((page - 1) * per_page).limit(per_page)
    return render_template("index.html",
                           recipes=recipe_page, pagination=pagination)


# Read individual recipe ingredients
@app.route("/get_recipes", methods=["GET"])
def get_recipes():
    recipes = mongo.db.recipes.find()
    return render_template("get_recipes.html", recipes=recipes)


# search query
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("index.html", recipes=recipes)


# User registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))
        # Register user info
        register = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
    return render_template("register.html")


# User Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)
        return redirect(url_for("login"))


# User Logout
@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("index"))


# About - introduction and quick explaination for CRUD ops
@app.route('/about')
def about():
    # about section with how to index and FAQ
    return render_template("about.html")


# Privacy policy
@app.route('/privacy')
def privacy():
    return render_template("privacy_policy.html")


@app.route('/listings')
def listings():
    per_page = 3
    page = request.args.get(get_page_parameter(), type=int, default=1)
    recipes = mongo.db.recipes.find().sort("timestamp", -1)
    pagination = Pagination(page=page, total=recipes.count(),
                            per_page=per_page,
                            search=False, record_name='recipes',
                            css_framework='bootstrap4', alignment='center')
    recipe_page = recipes.skip((page - 1) * per_page).limit(per_page)
    return render_template("listings.html",
                           recipes=recipe_page, pagination=pagination)


# Input is the Create id for the DB
@app.route("/input", methods=["GET", "POST"])
def input():
    # POST recipe to recipes DB
    if request.method == "POST":
        upload = {
            "timestamp": datetime.datetime.now(),
            "RecipeName": request.form.get("RecipeName"),
            "PrepTime": request.form.get("PrepTime"),
            "CookingTime": request.form.get("CookingTime"),
            "DifficultyLevel": request.form.get("DifficultyLevel"),
            "Serves": request.form.get("Serves"),
            "Ingredient": request.form.getlist("Ingredient"),
            "Add_ingredient": request.form.getlist("Ingredient"),
            "Qty": request.form.get("Qty"),
            "Instruction": request.form.getlist("Instruction"),
            "upload_pic": request.form.get("upload_pic"),
            "created_by": session["user"],
        }
        mongo.db.recipes.insert_one(upload)
        flash("Recipe Successfully added!")
    return render_template("input.html")


# Edit Recipes for id's in DB
@app.route("/edit_recipes/<recipes_id>", methods=["GET", "PUT"])
def edit_recipes(recipes_id):
    # Update recipe to recipes DB
    if request.method == "PUT":
        upload = {'$set': {
                  "timestamp": datetime.datetime.now(),
                  "RecipeName": request.form.get("RecipeName"),
                  "PrepTime": request.form.get("PrepTime"),
                  "CookingTime": request.form.get("CookingTime"),
                  "DifficultyLevel": request.form.get("DifficultyLevel"),
                  "Serves": request.form.get("Serves"),
                  "Ingredient": request.form.getlist("Ingredient"),
                  "Add_ingredient": request.form.getlist("Ingredient"),
                  "Qty": request.form.get("Qty"),
                  "Instruction": request.form.getlist("Instruction"),
                  "created_by": session["user"],
                  }}
        mongo.db.tasks.update_one({"_id": ObjectId(recipes_id)}, upload)
        flash("Task Successfully Updated")
    recipes = mongo.db.recipes.find_one({"_id": ObjectId(recipes_id)})
    return render_template("edit_recipes.html", recipes=recipes)


# Delete Recipes in DB
@app.route("/delete_recipes/<recipes_id>", methods=["GET"])
def delete_recipes(recipes_id):
    # Delete recipe to recipes DB
    mongo.db.recipes.delete_one({"_id": ObjectId(recipes_id)})
    recipes = mongo.db.recipes.find().sort("RecipeName", 1)
    flash("Recipe Successfully deleted!")
    return render_template("listings.html", recipes=recipes)


if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
