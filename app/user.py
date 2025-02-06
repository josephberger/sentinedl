from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import SessionLocal
from app.models import User

user_bp = Blueprint("user", __name__, url_prefix="/users")

@user_bp.route("/")
@login_required
def manage_users():
    """Allow users to view and manage users."""
    session = SessionLocal()
    users = session.query(User).all()
    session.close()
    
    return render_template("user_management.html", users=users)

@user_bp.route("/create", methods=["POST"])
@login_required
def create_user():
    """Allow admins to create new users."""
    username = request.form["username"].strip()
    password = request.form["password"].strip()

    # Username Validation
    if len(username) < 4:
        flash("Username must be at least 4 characters long.", "error")
        return redirect(url_for("user.manage_users"))
    if not username.isalnum():
        flash("Username must be alphanumeric with no special characters or spaces.", "error")
        return redirect(url_for("user.manage_users"))

    # Password Validation
    if len(password) < 6:
        flash("Password must be at least 6 characters long.", "error")
        return redirect(url_for("user.manage_users"))

    session = SessionLocal()
    existing_user = session.query(User).filter_by(username=username).first()

    if existing_user:
        session.close()
        flash("Username already exists.", "error")
        return redirect(url_for("user.manage_users"))

    # Create New User
    new_user = User(username=username, password_hash=generate_password_hash(password))
    session.add(new_user)
    session.commit()
    session.close()

    flash("User created successfully!", "success")
    return redirect(url_for("user.manage_users"))

@user_bp.route("/delete/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    """Allow admins to delete users."""
    if current_user.id == user_id:
        flash("You cannot delete yourself!", "error")
        return redirect(url_for("user.manage_users"))

    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()

    if not user:
        session.close()
        flash("User not found.", "error")
        return redirect(url_for("user.manage_users"))

    session.delete(user)
    session.commit()
    session.close()

    flash("User deleted successfully!", "success")
    return redirect(url_for("user.manage_users"))

@user_bp.route("/change_password", methods=["POST"])
@login_required
def change_password():
    """Allow users to change their own password."""
    current_password = request.form["current_password"].strip()
    new_password = request.form["new_password"].strip()

    # Validate new password
    if len(new_password) < 6:
        flash("New password must be at least 6 characters long.", "error")
        return redirect(url_for("user.manage_users"))

    session = SessionLocal()
    user = session.query(User).filter_by(id=current_user.id).first()

    # Verify current password
    if not check_password_hash(user.password_hash, current_password):
        session.close()
        flash("Current password is incorrect.", "error")
        return redirect(url_for("user.manage_users"))

    # Hash new password and update
    user.password_hash = generate_password_hash(new_password)
    session.commit()
    session.close()

    flash("Password changed successfully!", "success")
    return redirect(url_for("user.manage_users"))
