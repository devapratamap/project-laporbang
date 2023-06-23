import os
from os.path import join, dirname
from dotenv import load_dotenv

import jwt
import hashlib
# import requets
from flask import (Flask, render_template, jsonify, request, redirect, url_for)
from flask_pymongo import PyMongo
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = './static/profile'
app.config['UPLOAD_POST'] = './static/post'
app.config['UPLOAD_UPDATE_POST'] = './static/post'
app.config['UPLOAD_NEWS'] = './static/news'

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

TOKEN_KEY = 'mytoken'
SECRET_KEY = 'secret_pass'
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE'
}


@app.route('/', methods=['GET'])
def home():
    # Get token from browser cookie
    token_receive = request.cookies.get(TOKEN_KEY)
    # if token_receive is None:
    #     # Redirect user to login page if token is not present
    #     return redirect(url_for('home'))

    try:
        # Decode token using SECRET_KEY
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        # Get user info from database based on username in payload
        user_info = db.users.find_one({"username": payload["id"]})
        logged_in = True
        return render_template('index.html', logged_in=logged_in, user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        # return redirect(url_for('home', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('index.html', msg=msg)
    # return redirect(url_for('home', msg=msg))


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
        logged_in = True
        return render_template(
            'user.html',
            logged_in=logged_in,
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
    password_hash = hashlib.sha256(
        password_receive.encode('utf-8')).hexdigest()
    # Membuat dokumen baru yang akan disimpan ke dalam database
    doc = {
        "username": username_receive,
        "password": password_hash,
        "profile_name": username_receive,
        "profile_pic": "",
        "profile_pic_real": "assets/default-profile.png",
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


# @app.route('/update_profile', methods=['POST'])
# def save_img():
#     # Mendapatkan token dari cookie
#     token_receive = request.cookies.get("mytoken")
#     try:
#         # Mendekode token menggunakan SECRET_KEY
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
#         username = payload["id"]
#         # Mendapatkan data yang dikirimkan dalam permintaan POST
#         name_receive = request.form["name_give"]
#         about_receive = request.form["about_give"]
#         if "file_give" in request.files:
#             # Jika ada file yang dikirimkan, menyimpannya dan memperbarui path gambar profil
#             file = request.files["file_give"]
#             filename = secure_filename(file.filename)
#             extension = filename.split(".")[-1]
#             file_path = f"profile/{username}.{extension}"
#             file.save("./static/" + file_path)
#             new_doc["profile_pic"] = filename
#             new_doc["profile_pic_real"] = file_path
#         # Memperbarui informasi profil user dalam database
#         new_doc = {"profile_name": name_receive, "profile_info": about_receive}
#         db.users.update_one({"username": payload["id"]}, {"$set": new_doc})
#         return jsonify({"result": "success"})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))


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
        new_doc = {'profile_name': name_receive, 'profile_info': about_receive}
        if "file_give" in request.files:
            # Jika ada file yang dikirimkan, menyimpannya dan memperbarui path gambar profil
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile/{username}.jpg"
            file.save("./static/" + file_path)
            new_doc['profile_pic'] = filename
            new_doc['profile_pic_real'] = file_path
            # Memperbarui informasi gambar profil dalam dokumen MongoDB
            db.posts.update_many({"username": payload['id']}, {"$set": {"profile_pic": file_path}})
        db.users.update_one({"username": payload['id']}, {"$set": new_doc})
        db.posts.update_many({"username": payload['id']}, {
                             "$set": {'profile_name': name_receive}})
        return jsonify({"result": "success"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get(TOKEN_KEY)
    if token_receive is None:
        # Pengguna belum login, kembalikan ke halaman login
        return redirect(url_for('login'))
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"username": payload["id"]})
        alamat = request.form["alamat"]
        provinsi = request.form["provinsi"]
        kotakab = request.form["kotakab"]
        kecamatan = request.form["kecamatan"]
        deskripsi = request.form["deskripsi"]
        date_receive = request.form["date_give"]

        image = request.files['image']
        filename = image.filename

        # Save the image file to the specified folder
        image_path = os.path.join(app.config['UPLOAD_POST'], filename)
        image.save(image_path)

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
            "image_filename": filename
        }
        db.posts.insert_one(doc)
        return jsonify({
            'result': 'success',
            'msg': 'Posting success'
        }), 200, CORS_HEADERS
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('login')), 200, CORS_HEADERS


@app.route('/get_posts_all', methods=['GET'])
def get_posts_all():
    post = db.posts.find()
    post_list = []
    for postingan in post:
        post_list.append({
            "username": postingan["username"],
            "profile_name": postingan["profile_name"],
            "profile_pic_real": postingan["profile_pic_real"],
            "alamat": postingan["alamat"],
            "provinsi": postingan["provinsi"],
            "kotakab": postingan["kotakab"],
            "kecamatan": postingan["kecamatan"],
            "deskripsi": postingan["deskripsi"],
            "date": postingan["date"],
            "image_filename": postingan["image_filename"]
        })

    post_list = sorted(
        post_list, key=lambda postingan: postingan["date"], reverse=True)

    return jsonify(post_list), 200


@app.route('/get_posts', methods=['GET'])
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
                db.posts.find({"username": username_receive}
                              ).sort("date", -1).limit(20)
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
                    {"post_id": post["_id"], "type": "heart",
                        "username": payload["id"]}
                )
            )
            post["star_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "star",
                        "username": payload["id"]}
                )
            )
            post["thumbsup_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "thumbsup",
                        "username": payload["id"]}
                )
            )
        return jsonify({
            'result': 'success',
            'msg': 'Success fetched all post',
            "posts": posts
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

# @app.route('/update_post', methods=['POST'])
# def update_post():
#     # Mendapatkan token dari cookie
#     token_receive = request.cookies.get("mytoken")
#     try:
#         # Mendekode token menggunakan SECRET_KEY
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
#         username = payload["id"]
#         # Mendapatkan data yang dikirimkan dalam permintaan POST
#         alamat_receive = request.form["alamat_give"]
#         provinsi_receive = request.form["provinsi_give"]
#         kotakab_receive = request.form["kotakab_give"]
#         kecamatan_receive = request.form["kecamatan_give"]
#         deskripsi_receive = request.form["deskripsi_give"]
#         new_doc = {
#             "alamat": alamat_receive,
#             "provinsi": provinsi_receive,
#             "kotakab": kotakab_receive,
#             "kecamatan": kecamatan_receive,
#             "deskripsi": deskripsi_receive}
#         if "file_give" in request.files:
#             # Jika ada file yang dikirimkan, menyimpannya dan memperbarui path gambar profil
#             file = request.files["file_give"]
#             filename = secure_filename(file.filename)
#             extension = filename.split(".")[-1]
#             file_path = f"profile/{username}.{extension}"
#             file.save("./static/" + file_path)
#             new_doc["profile_pic"] = filename
#             new_doc["profile_pic_real"] = file_path
#         # Memperbarui informasi profil user dalam database
#         db.posts.update_one({"username": payload["id"]}, {"$set": new_doc})
#         return jsonify({"result": "success"})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))


@app.route('/news_posting', methods=['POST'])
def news_posting():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"username": payload["id"]})
        if user_info["username"] != "admlapor":
            return jsonify({
                'result': 'error',
                'msg': 'Unauthorized Access'
            }), 401
        
        judul = request.form["judul"]
        news_deskripsi = request.form["news_deskripsi"]
        date_receive = request.form["date_give"]

        image = request.files['file_name']
        filename = secure_filename(image.filename)

        # Save the image file to the specified folder
        image_path = os.path.join(app.config['UPLOAD_NEWS'], filename)
        image.save(image_path)

        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "judul": judul,
            "news_deskripsi": news_deskripsi,
            "date": date_receive,
            "image_filename": filename
        }
        db.news_posts.insert_one(doc)
        return jsonify({
            'result': 'success',
            'msg': 'Posting Berita Success'
        }), 200
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({
            'result': 'error',
            'msg': 'Token Expired or Invalid'
        }), 401



@app.route('/delete_post/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        db.posts.delete_one({"_id": ObjectId(post_id)})
        return jsonify({
            'result': 'success',
            'msg': 'Post deleted successfully'
        }), 200, CORS_HEADERS
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home')), 200, CORS_HEADERS


@app.route('/get_news_post', methods=['GET'])
def get_news_post():
    news_list = list(db.news_posts.find({}, {'_id': 0}))
    news_list = sorted(news_list, key=lambda news: news["date"], reverse=True)

    # Menambahkan URL gambar ke setiap entri dalam news_list
    for news in news_list:
        image_filename = news.get("image_filename")
        if image_filename:
            image_url = f"{request.host_url}static/news/{image_filename}"
            news["image_url"] = image_url

    return jsonify(news_list), 200


@app.route('/about', methods=['GET'])
def about():
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
        logged_in = True
        # logged_out = False
        return render_template('about.html', logged_in=logged_in, user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        # return redirect(url_for('home', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('about.html', msg=msg)
    # return redirect(url_for('home', msg=msg))


@app.route('/news', methods=['GET'])
def news():
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
        logged_in = True
        # logged_out = False
        return render_template('news.html', logged_in=logged_in, user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        # return redirect(url_for('home', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('news.html', msg=msg)
    # return redirect(url_for('home', msg=msg))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
