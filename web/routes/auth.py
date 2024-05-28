from flask import Blueprint, request, redirect, url_for
from flask_login import login_user, logout_user
from web import db
from web.models.Users import Users

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                     password=request.form.get("password"),
                     email=request.form.get("email"))
        db.session.add(user)
        db.session.commit()
    return redirect(url_for('web.index'))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        print(request.form.get("password"))
        if user and user.password == request.form.get("password"):
            login_user(user)
        return redirect(url_for('web.index'))

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("web.index"))
