from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for
)
from werkzeug.utils import secure_filename

app = Flask(__name__)

MONGODB_CONNECTION_STRING = 'mongodb+srv://deva:HikkyS123@cluster0.lqhsg9q.mongodb.net/?retryWrites=true&w=majority'

client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.dbprojectakhir

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')




if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)