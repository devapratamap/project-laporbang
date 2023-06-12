import os
from os.path import join, dirname
from dotenv import load_dotenv

import jwt
import hashlib
from flask import (Flask, render_template, jsonify, request, redirect, url_for)
from pymongo import MongoClient
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = './static/profile_pics'

SECRET_KEY = 'secret_pass'

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
TOKEN_KEY = 'mytoken'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home-admin')
def homeAdmin():
    return render_template('home-admin.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/profile-edit')
def profileEdit():
    return render_template('profile-edit.html')

@app.route('/berita')
def berita():
    return render_template('berita.html')

@app.route('/berita-admin')
def beritaAdmin():
    return render_template('berita-admin.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)