from flask import Blueprint, redirect, url_for, flash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import login_user, logout_user, login_required
from extensions import db

from models.user import User

auth = Blueprint('auth', __name__)

google_bp = make_google_blueprint(
    client_id=None,
    client_secret=None,
    scope=["profile", "email"],
    redirect_url="/login/google/authorized"
)

@auth.route('/login')
def login():
    return redirect(url_for('google.login'))

@auth.route('/login/google/authorized')
def google_authorized():
    if not google.authorized:
        flash('Failed to log in with Google.', 'danger')
        return redirect(url_for('auth.login'))

    resp = google.get('/oauth2/v2/userinfo')
    if not resp.ok:
        flash('Failed to fetch user info from Google.', 'danger')
        return redirect(url_for('auth.login'))

    info = resp.json()
    email = info['email']
    first_name = info.get('given_name', '')
    last_name = info.get('family_name', '')

    # Check if user already exists
    user = User.query.filter_by(email=email).first()

    # If not, create them automatically
    if not user:
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password='',
            role='user'
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('home'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))