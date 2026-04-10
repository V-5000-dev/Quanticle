from flask import Flask, render_template
from flask_login import current_user
from extensions import db, login_manager
from dotenv import load_dotenv
import os

load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.google_login'

@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('Quanticle.html', user=current_user)

with app.app_context():
    from routes.auth import auth
    app.register_blueprint(auth)
    from models.user import User
    db.create_all()

if __name__ == '__main__':
    app.run(port=os.getenv('FLASK_PORT', 3000), debug=True)