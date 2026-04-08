from flask import Flask, render_template
from flask_dance.contrib.google import make_google_blueprint
from dotenv import load_dotenv
from extensions import db, login_manager  # ← import from extensions
from routes.auth import auth
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)           # ← initialize with app
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

google_bp = make_google_blueprint(
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix='/login')
app.register_blueprint(auth)

@app.route('/')
def home():
    return render_template('Quanticle.html')

@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=os.getenv('FLASK_PORT', 3000), debug=True)