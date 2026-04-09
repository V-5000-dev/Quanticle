from flask import Blueprint, redirect, request, session
from flask_login import login_user, logout_user, login_required
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
import os
import hashlib
import base64
import secrets

auth = Blueprint('auth', __name__)

CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:3000/login/callback'

def make_flow(code_verifier=None):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email"
        ]
    )
    flow.redirect_uri = REDIRECT_URI
    if code_verifier:
        flow.code_verifier = code_verifier
    return flow

def generate_pkce():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()
    return code_verifier, code_challenge

@auth.route('/login/google')
def google_login():
    code_verifier, code_challenge = generate_pkce()
    session['code_verifier'] = code_verifier

    flow = make_flow()
    auth_url, state = flow.authorization_url(
        prompt='consent',
        access_type='offline',
        code_challenge=code_challenge,
        code_challenge_method='S256'
    )
    session['oauth_state'] = state
    return redirect(auth_url)

@auth.route('/login/callback')
def google_callback():
    from app import db
    from models.user import User

    try:
        code_verifier = session.get('code_verifier')
        print(f'=== CODE VERIFIER: {code_verifier} ===')

        flow = make_flow(code_verifier=code_verifier)
        flow.fetch_token(authorization_response=request.url)

        credentials = flow.credentials
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            grequests.Request(),
            CLIENT_ID
        )

        email = id_info.get('email')
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')

        print(f'=== GOOGLE INFO: {email}, {first_name} {last_name} ===')

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
            print('=== NEW USER CREATED ===')

        login_user(user)
        print(f'=== LOGGED IN: {user} ===')
        return redirect('/')

    except Exception as e:
        print(f'=== ERROR: {e} ===')
        return redirect('/')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')