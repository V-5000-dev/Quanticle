from flask import Flask, render_template
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
PORT = os.getenv('FLASK_PORT', 3000)

@app.route('/')
def home():
    return render_template('Quanticle.html')

if __name__ == '__main__':
    app.run(port=PORT, debug=True)