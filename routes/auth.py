from flask import Blueprint, redirect, flash
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    from flask_dance.contrib.google import google
    if not google.authorized:
        return redirect('/login/google')
    return redirect('/')

@auth.route('/login/google/authorized')
def google_authorized():
    from flask_dance.contrib.google import google
    from app import db
    from models.user import User

    print('=== GOOGLE AUTHORIZED ROUTE HIT ===')


    if not google.authorized:
        flash('Failed to log in with Google.', 'danger')
        return redirect('/')

    resp = google.get('/oauth2/v2/userinfo')
    if not resp.ok:
        flash('Failed to fetch user info.', 'danger')
        return redirect('/')

    info = resp.json()
    email = info['email']
    first_name = info.get('given_name', '')
    last_name = info.get('family_name', '')

    print(f'GOOGLE INFO: {email}, {first_name} {last_name}')

    user = User.query.filter_by(email=email).first()
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
        print('NEW USER CREATED')

    login_user(user)
    print('LOGGED IN:', user)
    return redirect('/')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')