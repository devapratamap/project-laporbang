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

@app.route('/', methods=['GET'])
def home():
    # Mendapatkan token dari cookie
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        # Mendekode token menggunakan SECRET_KEY
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        # Mendapatkan informasi user dari database berdasarkan username pada payload
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))
    
@app.route('/login', methods=['GET'])
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)


@app.route('/user/<username>', methods=['GET'])
def user(username):
    # Mendapatkan token dari cookie
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        # Mendekode token menggunakan SECRET_KEY
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        # Memeriksa apakah username dalam URL sama dengan username pada payload
        status = username == payload.get('id')
        # Mendapatkan informasi user dari database berdasarkan username
        user_info = db.users.find_one(
            {'username': username},
            {'_id': False}
        )
        return render_template(
            'user.html',
            user_info=user_info,
            status=status
        )
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))
    
    
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # Mendapatkan username dan password yang dikirimkan dalam permintaan POST
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    # Melakukan hashing pada password
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    # Mencari user yang sesuai dengan username dan password yang diberikan
    result = db.users.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )
    if result:
        # Jika user ditemukan, membuat token JWT dengan payload berisi informasi user
        payload = {
            "id": username_receive,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        # Mengembalikan respons JSON berisi token
        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    else:
        # Jika user tidak ditemukan, mengembalikan respons JSON dengan pesan kesalahan
        return jsonify(
            {
                "result": "fail",
                # "msg": "Kami tidak menemukan kombinasi Nama Pengguna/Kata Sandi tersebut",
            }
        )


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # Mendapatkan username dan password yang dikirimkan dalam permintaan POST
    username_receive = request.form.get('username_give')
    password_receive = request.form.get('password_give')
    # Melakukan hashing pada password
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # Membuat dokumen baru yang akan disimpan ke dalam database
    doc = {
        "username": username_receive,
        "password": password_hash,
        "profile_name": username_receive,
        "profile_pic": "",
        "profile_pic_real": "profile_pics/default.png",
        "profile_info": ""
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # Mendapatkan username yang dikirimkan dalam permintaan POST
    username_receive = request.form['username_give']
    # Memeriksa apakah username telah digunakan sebelumnya
    exists = bool(db.users.find_one({"username": username_receive}))
    # Mengembalikan respons JSON dengan hasil pengecekan
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/update_profile', methods=['POST'])
def save_img():
    # Mendapatkan token dari cookie
    token_receive = request.cookies.get("mytoken")
    try:
        # Mendekode token menggunakan SECRET_KEY
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        # Mendapatkan data yang dikirimkan dalam permintaan POST
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {"profile_name": name_receive, "profile_info": about_receive}
        if "file_give" in request.files:
            # Jika ada file yang dikirimkan, menyimpannya dan memperbarui path gambar profil
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        # Memperbarui informasi profil user dalam database
        db.users.update_one({"username": payload["id"]}, {"$set": new_doc})
        return jsonify({"result": "success"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
    
@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"username": payload["id"]})
        alamat = request.form["alamat"]
        provinsi = request.form["provinsi"]
        kotakab = request.form["kotakab"]
        kecamatan  = request.form["kecamatan"]
        deskripsi = request.form["deskripsi"]
        
        date_receive = request.form["date_give"]
        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "alamat": alamat,
            "provinsi": provinsi,
            "kotakab": kotakab,
            "kecamatan": kecamatan,
            "deskripsi": deskripsi,
            
            "date": date_receive,
        }
        db.posts.insert_one(doc)
        return jsonify({
            'result' : 'success',
            'msg' : 'Posting success'
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))
    
    
@app.route('/get_posts', methods = ['GET'])
def get_posts():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        username_receive = request.args.get("username_give")
        if username_receive == "":
            posts = list(db.posts.find({}).sort("date", -1).limit(20))
        else:
            posts = list(
                db.posts.find({"username": username_receive}).sort("date", -1).limit(20)
            )

        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "heart"}
            )
            post["count_star"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "star"}
            )
            post["count_thumbsup"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "thumbsup"}
            )
            post["heart_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "heart", "username": payload["id"]}
                )
            )
            post["star_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "star", "username": payload["id"]}
                )
            )
            post["thumbsup_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "thumbsup", "username": payload["id"]}
                )
            )
        return jsonify({
            'result' : 'success',
            'msg' : 'Success fetched all post',
            "posts": posts
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))
    
    
# @app.route('/post', methods=['POST'])
# def post():
#     alamat = request.form.get('alamat')
#     provinsi = request.form.get('provinsi')
#     kotakab = request.form.get('kotakab')
#     kecamatan = request.form.get('kecamatan')
#     deskripsi = request.form.get('deskripsi')
#     file = request.files['resume']

#     # Simpan file jika diperlukan
#     # file.save('path/to/save/file')

#     # Buat data postingan
#     posting_data = {
#         'alamat': alamat,
#         'provinsi': provinsi,
#         'kotakab': kotakab,
#         'kecamatan': kecamatan,
#         'deskripsi': deskripsi,
#         # Jika Anda menyimpan file, tambahkan path file ke dalam data postingan
#         # 'file_path': 'path/to/save/file'
#     }

#     # Simpan data postingan ke dalam MongoDB
#     result = collection.insert_one(posting_data)

#     return jsonify({'message': 'Postingan berhasil disimpan', 'post_id': str(result.inserted_id)})

    
    
    
    
@app.route('/about', methods=['GET'])
def about():
    # Mendapatkan token dari cookie
    token_receive = request.cookies.get(TOKEN_KEY)
    
    # Mendekode token menggunakan SECRET_KEY
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        # Tangani jika token sudah kadaluwarsa
        return redirect('/login')
    except jwt.InvalidTokenError:
        # Tangani jika token tidak valid
        return redirect('/login')

    # Mendapatkan informasi user dari database berdasarkan username pada payload
    user_info = db.users.find_one({"username": payload["id"]})
    if user_info:
        return render_template('about.html', user_info=user_info)
    else:
        # Tangani jika user tidak ditemukan
        return redirect('/login')
    
@app.route('/news', methods=['GET'])
def news():
    # Mendapatkan token dari cookie
    token_receive = request.cookies.get(TOKEN_KEY)
    
    # Mendekode token menggunakan SECRET_KEY
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        # Tangani jika token sudah kadaluwarsa
        return redirect('/login')
    except jwt.InvalidTokenError:
        # Tangani jika token tidak valid
        return redirect('/login')

    # Mendapatkan informasi user dari database berdasarkan username pada payload
    user_info = db.users.find_one({"username": payload["id"]})
    if user_info:
        return render_template('news.html', user_info=user_info)
    else:
        # Tangani jika user tidak ditemukan
        return redirect('/login')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)