from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "c60a1f887b625600bb7f2f45aca3f53e635b1677"
app.config["MONGO_URI"] = "mongodb+srv://m4bbarhoom:M.0991987847b@cluster0.o6ukn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

mongo = PyMongo(app)
users_collection = mongo.cx['auth_database'].users







# Login route (renders authentication form)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("profile"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html")

# Registration route (advanced feature)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Check if user already exists
        if users_collection.find_one({"username": username}):
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))
        hashed_password = generate_password_hash(password)
        # Use a default profile picture (ensure the file exists in static/images)
        default_pic = url_for('static', filename='images/default_user_icon.png')
        new_user = {
            "username": username,
            "password": hashed_password,
            "profile_pic": default_pic,
            "info": {}  # additional profile information
        }
        users_collection.insert_one(new_user)
        flash("Account created successfully! Please log in.", "success")
        # (Optional Challenge: Notify active users about the new account)
        return redirect(url_for("login"))
    return render_template("register.html")

# Protected profile page (only for authenticated users)
@app.route("/profile")
def profile():
    if "user" not in session:
        flash("Please log in to view your profile", "warning")
        return redirect(url_for("login"))
    username = session["user"]
    user = users_collection.find_one({"username": username})
    if not user:
        flash("User not found", "danger")
        return redirect(url_for("login"))
    return render_template("profile.html", user=user)

# Logout route
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))

# Change password route (advanced feature)
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "user" not in session:
        flash("Please log in", "warning")
        return redirect(url_for("login"))
    username = session["user"]
    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user["password"], current_password):
            new_hashed = generate_password_hash(new_password)
            users_collection.update_one({"username": username}, {"$set": {"password": new_hashed}})
            flash("Password updated successfully", "success")
            return redirect(url_for("profile"))
        else:
            flash("Current password is incorrect", "danger")
    return render_template("change_password.html")

# Update profile route (advanced feature: update info and profile picture)
@app.route("/update_profile", methods=["GET", "POST"])
def update_profile():
    if "user" not in session:
        flash("Please log in", "warning")
        return redirect(url_for("login"))
    username = session["user"]
    user = users_collection.find_one({"username": username})
    if request.method == "POST":
        info = {
            "full_name": request.form.get("full_name"),
            "bio": request.form.get("bio"),
            "email": request.form.get("email")
        }
        # Handle profile picture upload if provided
        if "profile_pic" in request.files:
            pic = request.files["profile_pic"]
            if pic.filename != "":
                pic_filename = f"{username}_profile.png"
                pic_path = os.path.join(app.root_path, "static", "images", pic_filename)
                pic.save(pic_path)
                profile_pic_url = url_for('static', filename=f'images/{pic_filename}')
                users_collection.update_one({"username": username}, {"$set": {"profile_pic": profile_pic_url}})
        users_collection.update_one({"username": username}, {"$set": {"info": info}})
        flash("Profile updated successfully", "success")
        return redirect(url_for("profile"))
    return render_template("update_profile.html", user=user)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
