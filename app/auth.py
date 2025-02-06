from flask import Blueprint, request, redirect, url_for, render_template, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from app.database import SessionLocal
from app.models import User

auth_bp = Blueprint("auth", __name__)

# Initialize JWT Manager (will be configured in app init)
jwt = JWTManager()

login_manager = LoginManager()
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    session = SessionLocal()
    user = session.query(User).get(int(user_id))
    session.close()
    return user

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        session = SessionLocal()
        user = session.query(User).filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            session.close()
            flash("Invalid username or password.", "error")
            return redirect(url_for("auth.login"))

        login_user(user)
        session.close()

        flash("Login successful!", "success")
        return redirect(url_for("edl.home"))

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    """Authenticate user and return JWT token."""
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    session = SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    session.close()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Create JWT token
    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200