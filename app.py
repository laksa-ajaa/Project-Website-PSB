import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, url_for, redirect, flash, make_response
import jwt
from bson.objectid import ObjectId
import hashlib
from pymongo import MongoClient
from datetime import datetime, timedelta
from pathlib import Path
from flask_paginate import Pagination, get_page_parameter
import bleach

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

SECRET_KEY = os.environ.get("SECRET_KEY") 
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_DOKUMEN"] = "static/santri/dokumen"
app.config["UPLOAD_PEMBAYARAN"] = "static/santri/pembayaran"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# AUTH USER BACKEND
@app.route('/auth')
def showAuth():
    data = {
        'title': 'Login/Register',
    }
    token = request.cookies.get('tokenLogin')
    if token:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return redirect(url_for('showDashUser'))
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            pass
    
    return render_template('auth/login.html', data=data)

@app.route('/login', methods=['POST'])
def auth():
    email = bleach.clean(request.form["email"])
    password = bleach.clean(request.form["password"])
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    user = db.users.find_one({"email": email})
    if user:
        if user['password'] == password_hash:
            payload = {
                "_id": str(user["_id"]),
                "exp": datetime.utcnow() + timedelta(hours=1),
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            response = make_response(jsonify({"status": "success", "msg": "Login Berhasil!"}))
            response.set_cookie("tokenLogin", token)
            return response
        else:
            return jsonify({"status": "error", "msg": "Password salah"})
    else:
        return jsonify({"status": "error", "msg": "Email tidak terdaftar"})

@app.route('/register', methods = ["post"])
def register():
    nama = bleach.clean(request.form["nama"])
    email = bleach.clean(request.form["email"])
    phone = bleach.clean(request.form["phone"])
    password = bleach.clean(request.form["password"])
    
    cek_email = db.users.find_one({"email": email})
    if cek_email:
        return jsonify({"status": "error", "msg": "Email sudah terdaftar"})
    
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    doc = {
        "nama": nama,
        "email": email,
        "phone": phone,
        "password": password_hash,
        "status formulir": "None",
        "status dokumen": "None",
        "status pembayaran": "None",
        "program": "",
    }
    db.users.insert_one(doc)
    return jsonify({"status": "success"})

@app.route('/logout')
def logout():
    flash("Anda telah logout", "success")
    response = make_response(redirect(url_for('showAuth')))
    response.delete_cookie("tokenLogin")
    return response

#USER PAGE ROUTES
@app.route('/')
def showHome():
    data = {
        'title': 'Beranda',
    }
    token_receive = request.cookies.get("tokenLogin")
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"_id": ObjectId(payload["_id"])})
            admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"])})
            return render_template('user_page/index.html', data=data, user_info=user_info, admin_info=admin_info)
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            response = make_response(redirect(url_for('showHome')))
            response.delete_cookie("tokenLogin")
            return response
    else:
        return render_template('user_page/index.html', data=data)
        
@app.route('/sejarah')
def showSejarah():
    data = {
        "title": "Ulumul Qur'an | Sejarah",
    }
    token_receive = request.cookies.get("tokenLogin")
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"_id": ObjectId(payload["_id"])})
            admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"])})
            return render_template('user_page/sejarah.html', data=data, user_info=user_info, admin_info=admin_info)
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            response = make_response(redirect(url_for('showHome')))
            response.delete_cookie("tokenLogin")
            return response
    else:
        return render_template('user_page/sejarah.html', data=data)

@app.route('/kontak')
def showKontak():
    data = {
        "title": "Ulumul Qur'an | Kontak",
    }
    token_receive = request.cookies.get("tokenLogin")
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"_id": ObjectId(payload["_id"])})
            admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"])})
            return render_template('user_page/kontak.html', data=data, user_info=user_info, admin_info=admin_info)
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            response = make_response(redirect(url_for('showHome')))
            response.delete_cookie("tokenLogin")
            return response
    else:
        return render_template('user_page/kontak.html' , data=data)

@app.route('/visimisi')
def showVisiMisi():
    data = {
        "title": "Ulumul Qur'an | Visi & Misi",
    }
    token_receive = request.cookies.get("tokenLogin")
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"_id": ObjectId(payload["_id"])})
            admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"])})
            return render_template('user_page/visimisi.html', data=data, user_info=user_info, admin_info=admin_info)
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            response = make_response(redirect(url_for('showHome')))
            response.delete_cookie("tokenLogin")
            return response
    else:
        return render_template('user_page/visimisi.html' , data=data)

@app.route('/kegiatan')
def showKegiatan():
    data = {
        "title": "Ulumul Qur'an | Kegiatan & Fasilitas",
    }
    token_receive = request.cookies.get("tokenLogin")
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"_id": ObjectId(payload["_id"])})
            admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"])})
            return render_template('user_page/kegiatan.html', data=data, user_info=user_info, admin_info=admin_info)
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            response = make_response(redirect(url_for('showHome')))
            response.delete_cookie("tokenLogin")
            return response
    else:
        return render_template('user_page/kegiatan.html' , data=data)

# ADMIN AUTH BACKEND
@app.route('/authAdmin', methods=["GET", "POST"])
def authAdmin():
    data = {
        'title': 'Login Admin',
    }
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        cek_login = db.admin.find_one({"username": username, "password": password_hash})
        if cek_login:
            if cek_login.get("role") == "admin":
                payload = {
                    "_id": str(cek_login["_id"]),
                    "role": "admin",
                    "exp": datetime.utcnow() + timedelta(hours=1)
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                response = make_response(redirect(url_for('indexAdmin')))
                response.set_cookie("tokenLogin", token, httponly=True)
                return response
            else:
                return jsonify({"status": "error", "msg": "Anda tidak memiliki izin untuk mengakses halaman ini"}), 403
        else:
            return jsonify({"status": "error", "msg": "Username atau password salah"}), 401
    return render_template('auth/login_admin.html', data=data)

@app.route('/admin/logout')
def logout_admin():
    flash("Anda telah logout", "success")
    response = make_response(redirect(url_for('authAdmin')))
    response.delete_cookie("tokenLogin")
    return response

# DASHBOARD ADMIN ROUTES
@app.route('/admin')
def indexAdmin():
    data = {
        'title': 'Dashboard Admin',
        'active': 'home',
        
    }
    token_receive = request.cookies.get("tokenLogin")

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] == "admin":
            data['pendaftar'] = list(db.users.find({}).sort([("_id", -1)]).limit(5))
            data['total_pendaftar'] = list(db.users.find({}))
            data['mts'] = list(db.users.find({ "program": "MTs" }))
            data['mas'] = list(db.users.find({ "program": "MAS" }))
            data['form'] = list(db.form.find({}))
            data['doc'] = list(db.dokumen_santri.find({}))
            data['pembayaran'] = list(db.pembayaran.find({}))
            
            return render_template("dashboard_admin/index.html", admin_info=admin_info, data=data)
        else:
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response

    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/pendaftar')
def pesertaAdmin():
    data = {
        'title': 'Dashboard Admin',
        'active': 'pendaftar'
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] == "admin":
            
            page = request.args.get(get_page_parameter(), type=int, default=1)
            per_page = 10  # Jumlah data per halaman
            offset = (page - 1) * per_page

            # Mengambil data user dan mengurutkan berdasarkan _id secara descending dan membatasi hasil
            users = db.users.find().sort("_id", -1).skip(offset).limit(per_page)
            
            # Konversi data ke list agar bisa dijadikan JSON
            user_list = []
            for user in users:
                user['_id'] = str(user['_id'])  # Konversi ObjectId ke string
                user_list.append(user)

            # Menghitung total jumlah user
            total_users = db.users.count_documents({})

            # Membuat objek pagination
            pagination = Pagination(page=page, total=total_users, per_page=per_page, record_name='users')
            return render_template("dashboard_admin/pendaftar.html", admin_info=admin_info, data=data, users=user_list, pagination=pagination, offset=offset)
        else:
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

#VERIFIKASI FORMULIR MA
@app.route('/admin/formulir/aliyah', methods=['GET'])
def verifyFormulirMA():
    data = {
        'title': 'Dashboard Admin',
        'active': 'verifikasi_ma'
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        # Mendapatkan data siswa yang sedang menunggu verifikasi
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 10  # Jumlah data per halaman
        offset = (page - 1) * per_page

        # Mengambil data user dan mengurutkan berdasarkan _id secara descending dan membatasi hasil
        users = db.users.find({'program': 'MAS'}).sort("tanggal pendaftaran", -1).skip(offset).limit(per_page)
        
        # Konversi data ke list agar bisa dijadikan JSON
        user_list = []
        for user in users:
            user['_id'] = str(user['_id'])  # Konversi ObjectId ke string
            user_list.append(user)

        # Menghitung total jumlah user
        total_users = db.users.count_documents({'program': 'MAS', 'status formulir': {'$ne': 'None'}})

        # Membuat objek pagination
        pagination = Pagination(page=page, total=total_users, per_page=per_page, record_name='users')
                
        return render_template("dashboard_admin/formulir_ma.html", admin_info=admin_info, data=data, users=user_list, pagination=pagination, offset=offset)

    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/formulir/aliyah/<id>', methods=['POST'])
def approveFormulirMA(id):
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status formulir': 'Done', 'tolak_form': ''}})
        return redirect(url_for("verifyFormulirMA"))
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/formulir/aliyah/reject/<id>', methods=['POST'])
def rejectFormulirMA(id):
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        data = request.get_json()
        rejection_message = data.get('rejectionMessage')
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status formulir': 'Rejected', 'tolak_form': rejection_message, 'tanggal pendaftaran': ''}})
        db.form.delete_one({'user_id': ObjectId(id)})
        return jsonify({'message': 'Formulir telah ditolak.'}), 200
    
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response
    except Exception as e:
        return jsonify({'message': 'Terjadi kesalahan, silahkan coba lagi.'}), 500

@app.route('/admin/formulir/aliyah/<id>')
def detailFormulirMA(id):
    data = {
        'title': 'Detail Formulir',
        'active': 'verifikasi_ma'
    }
    token_receive = request.cookies.get("tokenLogin")
    
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        user_form = db.form.find_one({"user_id": ObjectId(id)})
        user_info = db.users.find_one({"_id": ObjectId(id)})
        return render_template("dashboard_admin/form_detail_ma.html", data=data, user_form=user_form , admin_info=admin_info, user_info=user_info)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

#VERIFIKASI DOKUMEN MA
@app.route('/admin/dokumen/aliyah', methods=['GET'])
def verifyDokumenMA():
    data = {
        'title': 'Dashboard Admin',
        'active': 'verifikasi_ma'
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 10  # Jumlah data per halaman
        offset = (page - 1) * per_page

        # Mengambil data user dan mengurutkan berdasarkan _id secara descending dan membatasi hasil
        users = db.users.find({'program': 'MAS'}).sort("tanggal upload dokumen", -1).skip(offset).limit(per_page)
        
        # Konversi data ke list agar bisa dijadikan JSON
        user_list = []
        for user in users:
            user['_id'] = str(user['_id'])  # Konversi ObjectId ke string
            user_list.append(user)

        # Menghitung total jumlah user
        total_users = db.users.count_documents({'program': 'MAS', 'status dokumen': {'$ne': 'None'}})

        # Membuat objek pagination
        pagination = Pagination(page=page, total=total_users, per_page=per_page, record_name='users')
        
        return render_template("dashboard_admin/dokumen_ma.html", admin_info=admin_info, data=data, users=user_list, pagination=pagination, offset=offset)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/dokumen/aliyah/<id>')
def detailDokumenMA(id):
    data = {
        'title': 'Detail Dokumen',
        'active': 'verifikasi_ma'
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        user_doc = db.dokumen_santri.find_one({"user_id": ObjectId(id)})
        user_info = db.users.find_one({"_id": ObjectId(id)})
        return render_template("dashboard_admin/doc_detail_ma.html", data=data, user_doc=user_doc , user_info=user_info, admin_info=admin_info)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response 

@app.route('/admin/dokumen/aliyah/<id>', methods=['POST'])
def approveDokumenMA(id):
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status dokumen': 'Done', 'tolak_doc': ''}})
        return redirect(url_for("verifyDokumenMA"))
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/dokumen/aliyah/reject/<id>', methods=['POST'])
def rejectDokumenMA(id):
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        data = request.get_json()
        rejection_message = data.get('rejectionMessage')
        
        user_doc = db.dokumen_santri.find_one({'user_id': ObjectId(id)})
        if not user_doc:
            return jsonify({'message': 'Dokumen tidak ditemukan.'}), 404
        
        file_keys = ['pas_foto', 'ijazah', 'surat_keterangan_lulus', 'akta_kelahiran', 'kartu_keluarga', 'surat_memiliki_nisn']
        
        for key in file_keys:
            if key in user_doc:
                file_path = user_doc[key].replace('/static/santri/dokumen/', '')
                full_path = os.path.join('static/santri/dokumen', file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
        
        db.users.update_one({'_id': ObjectId(id)}, {'$set'  : {'status dokumen': 'Rejected', 'tolak_doc': rejection_message, 'tanggal upload dokumen': ''}})
        db.dokumen_santri.delete_one({'user_id': ObjectId(id)})
        
        return jsonify({'message': 'Dokumen telah ditolak.'}), 200
    
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response
    except Exception as e:
        return jsonify({'message': 'Terjadi kesalahan, silahkan coba lagi.'}), 500

#VERIFIKASI PEMBAYARAN MA
@app.route('/admin/pembayaran/aliyah', methods=['GET'])
def verifyPembayaranMA():
    data = {
        'title': 'Dashboard Admin',
        'active': 'verifikasi_ma'
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        # Mendapatkan data siswa yang sedang menunggu verifikasi
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 10  # Jumlah data per halaman
        offset = (page - 1) * per_page

        # Mengambil data user dan mengurutkan berdasarkan _id secara descending dan membatasi hasil
        users = db.users.find({'program': 'MAS'}).sort("tanggal bayar", -1).skip(offset).limit(per_page)
        
        # Konversi data ke list agar bisa dijadikan JSON
        user_list = []
        for user in users:
            user['_id'] = str(user['_id'])  # Konversi ObjectId ke string
            user_list.append(user)

        # Menghitung total jumlah user
        total_users = db.users.count_documents({'program': 'MAS', 'status pembayaran': {'$ne': 'None'}})

        # Membuat objek pagination
        pagination = Pagination(page=page, total=total_users, per_page=per_page, record_name='users')
        
        return render_template("dashboard_admin/pembayaran_ma.html", admin_info=admin_info, data=data, users=user_list, pagination=pagination, offset=offset)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/pembayaran/aliyah/<id>')
def detailPembayaranMA(id):
    data = {
        'title': 'Detail Pembayaran',
        'active': 'verifikasi_ma'
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        user_pay = db.pembayaran.find_one({"user_id": ObjectId(id)})
        user_info = db.users.find_one({"_id": ObjectId(id)})
        return render_template("dashboard_admin/pay_detail_ma.html", data=data, user_pay=user_pay, user_info=user_info, admin_info=admin_info)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/pembayaran/aliyah/<id>', methods=['POST'])
def approvePembayaranMA(id):
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status pembayaran': 'Done', 'tolak_pay' : ''}})
        return redirect(url_for("verifyPembayaranMA"))
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/pembayaran/aliyah/reject/<id>', methods=['POST'])
def rejectPembayaranMA(id):
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        data = request.get_json()
        rejection_message = data.get('rejectionMessage')
        
        user_pay = db.pembayaran.find_one({'user_id': ObjectId(id)})
        if not user_pay:
            return jsonify({'message': 'Pembayaran tidak ditemukan.'}), 404
        
        file_path = user_pay['foto bukti'].replace('/static/santri/pembayaran/', '')
        full_path = os.path.join('static/santri/pembayaran', file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
        
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status pembayaran': 'Rejected', 'tolak_pay': rejection_message, 'tanggal bayar': ''}})
        db.pembayaran.delete_one({'user_id': ObjectId(id)})
        
        return jsonify({'message': 'Pembayaran telah ditolak.'}), 200
    
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response
    except Exception as e:
        return jsonify({'message': 'Terjadi kesalahan, silahkan coba lagi.'}), 500

#VERIFIKASI FORMULIR MTS
@app.route('/admin/formulir/tsanawiyah', methods=['GET'])
def verifyFormulirMTS():
    data = {
        'title': 'Dashboard Admin',
        'active': 'verifikasi_mts'
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        # Mendapatkan data siswa yang sedang menunggu verifikasi
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 10  # Jumlah data per halaman
        offset = (page - 1) * per_page

        # Mengambil data user dan mengurutkan berdasarkan _id secara descending dan membatasi hasil
        users = db.users.find({'program': 'MTs'}).sort("tanggal pendaftaran", -1).skip(offset).limit(per_page)
        
        # Konversi data ke list agar bisa dijadikan JSON
        user_list = []
        for user in users:
            user['_id'] = str(user['_id'])  # Konversi ObjectId ke string
            user_list.append(user)

        # Menghitung total jumlah user
        total_users = db.users.count_documents({'program': 'MTs', 'status formulir': {'$ne': 'None'}})

        # Membuat objek pagination
        pagination = Pagination(page=page, total=total_users, per_page=per_page, record_name='users')
                
        return render_template("dashboard_admin/formulir_mts.html", admin_info=admin_info, data=data, users=user_list, pagination=pagination, offset=offset)

    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/formulir/tsanawiyah/<id>', methods=['POST'])
def approveFormulirMTS(id):
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status formulir': 'Done', 'tolak_form': ''}})
        return redirect(url_for("verifyFormulirMTS"))
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/formulir/tsanawiyah/reject/<id>', methods=['POST'])
def rejectFormulirMTS(id):
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        data = request.get_json()
        rejection_message = data.get('rejectionMessage')
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status formulir': 'Rejected', 'tolak_form': rejection_message, 'tanggal pendaftaran': ''}})
        db.form.delete_one({'user_id': ObjectId(id)})
        return jsonify({'message': 'Formulir telah ditolak.'}), 200
    
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response
    except Exception as e:
        return jsonify({'message': 'Terjadi kesalahan, silahkan coba lagi.'}), 500

@app.route('/admin/formulir/tsanawiyah/<id>')
def detailFormulirMTS(id):
    data = {
        'title': 'Detail Formulir',
        'active': 'verifikasi_mts'
    }
    token_receive = request.cookies.get("tokenLogin")
    
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        user_form = db.form.find_one({"user_id": ObjectId(id)})
        user_info = db.users.find_one({"_id": ObjectId(id)})
        return render_template("dashboard_admin/form_detail_mts.html", data=data, user_form=user_form , admin_info=admin_info, user_info=user_info)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

#VERIFIKASI DOKUMEN MTS
@app.route('/admin/dokumen/tsanawiyah', methods=['GET'])
def verifyDokumenMTS():
    data = {
        'title': 'Dashboard Admin',
        'active': 'verifikasi_mts'
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 10  # Jumlah data per halaman
        offset = (page - 1) * per_page

        # Mengambil data user dan mengurutkan berdasarkan _id secara descending dan membatasi hasil
        users = db.users.find({'program': 'MTs'}).sort("tanggal upload dokumen", -1).skip(offset).limit(per_page)
        
        # Konversi data ke list agar bisa dijadikan JSON
        user_list = []
        for user in users:
            user['_id'] = str(user['_id'])  # Konversi ObjectId ke string
            user_list.append(user)

        # Menghitung total jumlah user
        total_users = db.users.count_documents({'program': 'MTs', 'status dokumen': {'$ne': 'None'}})

        # Membuat objek pagination
        pagination = Pagination(page=page, total=total_users, per_page=per_page, record_name='users')
        
        return render_template("dashboard_admin/dokumen_mts.html", admin_info=admin_info, data=data, users=user_list, pagination=pagination, offset=offset)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/dokumen/tsanawiyah/<id>')
def detailDokumenMTS(id):
    data = {
        'title': 'Detail Dokumen',
        'active': 'verifikasi_mts'
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        user_doc = db.dokumen_santri.find_one({"user_id": ObjectId(id)})
        user_info = db.users.find_one({"_id": ObjectId(id)})
        return render_template("dashboard_admin/doc_detail_mts.html", data=data, user_doc=user_doc , user_info=user_info, admin_info=admin_info)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response 

@app.route('/admin/dokumen/tsanawiyah/<id>', methods=['POST'])
def approveDokumenMTS(id):
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status dokumen': 'Done', 'tolak_doc': ''}})
        return redirect(url_for("verifyDokumenMTS"))
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/dokumen/tsanawiyah/reject/<id>', methods=['POST'])
def rejectDokumenMTS(id):
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        data = request.get_json()
        rejection_message = data.get('rejectionMessage')
        
        user_doc = db.dokumen_santri.find_one({'user_id': ObjectId(id)})
        if not user_doc:
            return jsonify({'message': 'Dokumen tidak ditemukan.'}), 404
        
        file_keys = ['pas_foto', 'ijazah', 'surat_keterangan_lulus', 'akta_kelahiran', 'kartu_keluarga', 'surat_memiliki_nisn']
        
        for key in file_keys:
            if key in user_doc:
                file_path = user_doc[key].replace('/static/santri/dokumen/', '')
                full_path = os.path.join('static/santri/dokumen', file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
        
        db.users.update_one({'_id': ObjectId(id)}, {'$set'  : {'status dokumen': 'Rejected', 'tolak_doc': rejection_message, 'tanggal upload dokumen': ''}})
        db.dokumen_santri.delete_one({'user_id': ObjectId(id)})
        
        return jsonify({'message': 'Dokumen telah ditolak.'}), 200
    
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response
    except Exception as e:
        return jsonify({'message': 'Terjadi kesalahan, silahkan coba lagi.'}), 500

#VERIFIKASI PEMBAYARAN MTS
@app.route('/admin/pembayaran/tsanawiyah', methods=['GET'])
def verifyPembayaranMTS():
    data = {
        'title': 'Dashboard Admin',
        'active': 'verifikasi_mts'
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        # Mendapatkan data siswa yang sedang menunggu verifikasi
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 10  # Jumlah data per halaman
        offset = (page - 1) * per_page

        # Mengambil data user dan mengurutkan berdasarkan _id secara descending dan membatasi hasil
        users = db.users.find({'program': 'MTs'}).sort("tanggal bayar", -1).skip(offset).limit(per_page)
        
        # Konversi data ke list agar bisa dijadikan JSON
        user_list = []
        for user in users:
            user['_id'] = str(user['_id'])  # Konversi ObjectId ke string
            user_list.append(user)

        # Menghitung total jumlah user
        total_users = db.users.count_documents({'program': 'MTs', 'status pembayaran': {'$ne': 'None'}})

        # Membuat objek pagination
        pagination = Pagination(page=page, total=total_users, per_page=per_page, record_name='users')
        
        return render_template("dashboard_admin/pembayaran_mts.html", admin_info=admin_info, data=data, users=user_list, pagination=pagination, offset=offset)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/pembayaran/tsanawiyah/<id>')
def detailPembayaranMTS(id):
    data = {
        'title': 'Detail Pembayaran',
        'active': 'verifikasi_mts'
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"_id": ObjectId(payload["_id"]), "role": payload["role"]})
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        user_pay = db.pembayaran.find_one({"user_id": ObjectId(id)})
        user_info = db.users.find_one({"_id": ObjectId(id)})
        return render_template("dashboard_admin/pay_detail_mts.html", data=data, user_pay=user_pay, user_info=user_info, admin_info=admin_info)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/pembayaran/tsanawiyah/<id>', methods=['POST'])
def approvePembayaranMTS(id):
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status pembayaran': 'Done', 'tolak_pay' : ''}})
        return redirect(url_for("verifyPembayaranMTS"))
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/admin/pembayaran/tsanawiyah/reject/<id>', methods=['POST'])
def rejectPembayaranMTS(id):
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        data = request.get_json()
        rejection_message = data.get('rejectionMessage')
        
        user_pay = db.pembayaran.find_one({'user_id': ObjectId(id)})
        if not user_pay:
            return jsonify({'message': 'Pembayaran tidak ditemukan.'}), 404
        
        file_path = user_pay['foto bukti'].replace('/static/santri/pembayaran/', '')
        full_path = os.path.join('static/santri/pembayaran', file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
        
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status pembayaran': 'Rejected', 'tolak_pay': rejection_message, 'tanggal bayar': ''}})
        db.pembayaran.delete_one({'user_id': ObjectId(id)})
        
        return jsonify({'message': 'Pembayaran telah ditolak.'}), 200
    
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response
    except Exception as e:
        return jsonify({'message': 'Terjadi kesalahan, silahkan coba lagi.'}), 500


# DASHBOARD USER ROUTES
@app.route('/dashboard')
def showDashUser():
    data = {
        'title': 'Dashboard',
    }
    token_receive = request.cookies.get("tokenLogin")
    if not token_receive:
        flash("Silahkan login terlebih dahulu", "danger")
        return redirect(url_for("showAuth"))

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' in payload and payload['role'] == 'admin':
            flash("Halaman ini tidak dapat diakses oleh admin", "danger")
            return redirect(url_for("indexAdmin"))

        user_info = db.users.find_one({"_id": ObjectId(payload["_id"])})
        if not user_info:
            flash("User tidak ditemukan", "danger")
            return redirect(url_for("showAuth"))
        return render_template("dashboard_user/index.html", user_info=user_info, data=data)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

# DASHBOARD FORMULIR ROUTES
@app.route('/dashboard/formulir', methods=["GET", "POST"])
def showformulir():
    data = {
        'title': 'Formulir',
    }
    token_receive = request.cookies.get("tokenLogin")
    if not token_receive:
        flash("Silahkan login terlebih dahulu", "danger")
        return redirect(url_for("showAuth"))

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' in payload and payload['role'] == 'admin':
            flash("Halaman ini tidak dapat diakses oleh admin", "danger")
            return redirect(url_for("indexAdmin"))
        
        user_info = db.users.find_one({"_id": ObjectId(payload["_id"])})
        if not user_info:
            flash("User tidak ditemukan", "danger")
            return redirect(url_for("showAuth"))
        
        existing_form = db.form.find_one({"user_id": user_info["_id"]})
        form_submitted = bool(existing_form)
        
        if request.method == "POST" and not form_submitted:
            data = {
                "user_id": user_info["_id"],
                "nama": bleach.clean(request.form["nama"]),
                "tempat lahir": bleach.clean(request.form["tempat_lahir"]),
                "tanggal lahir": bleach.clean(request.form["tanggal_lahir"]),
                "jenis kelamin": bleach.clean(request.form["jenis_kelamin"]),
                "alamat": bleach.clean(request.form["alamat"]),
                "NISN": bleach.clean(request.form["nisn"]),
                "sekolah asal": bleach.clean(request.form["sekolah_asal"]),
                "pendidikan": bleach.clean(request.form["pendidikan"]),
                "program": bleach.clean(request.form["program"]),
                "nama ibu": bleach.clean(request.form["nama_ibu"]),
                "nik ibu": bleach.clean(request.form["nik_ibu"]),
                "tempat lahir ibu": bleach.clean(request.form["tempat_lahir_ibu"]),
                "tanggal lahir ibu": bleach.clean(request.form["tanggal_lahir_ibu"]),
                "no telepon ibu": bleach.clean(request.form["no_hp_ibu"]),
                "nama ayah": bleach.clean(request.form["nama_ayah"]),
                "nik ayah": bleach.clean(request.form["nik_ayah"]),
                "tempat lahir ayah": bleach.clean(request.form["tempat_lahir_ayah"]),
                "tanggal lahir ayah": bleach.clean(request.form["tanggal_lahir_ayah"]),
                "no telepon ayah": bleach.clean(request.form["no_hp_ayah"]),
                "tanggal pendaftaran": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }

            db.form.insert_one(data)

            db.users.update_one(
                {"_id": ObjectId(user_info["_id"])},
                {
                    "$set": {
                        "status formulir": "Pending",
                        "nama": data["nama"],
                        "tanggal pendaftaran": data["tanggal pendaftaran"],
                        "program": data["program"],
                    }
                }
            )
            flash('Formulir berhasil dikirim', 'success')
            return redirect(url_for('showformulir'))
        else:
            return render_template('dashboard_user/formulir.html', data=data, user_info=user_info, form_submitted=form_submitted)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

# DASHBOARD DOKUMEN ROUTES
@app.route('/dashboard/dokumen', methods=["GET", "POST"])
def showdoc():
    data = {
        'title': 'Upload Dokumen',
    }
    token_receive = request.cookies.get("tokenLogin")
    if not token_receive:
        flash("Silahkan login terlebih dahulu", "danger")
        return redirect(url_for("showAuth"))

    try:
        payload = jwt.decode(token_receive, app.config['SECRET_KEY'], algorithms=["HS256"])
        if 'role' in payload and payload['role'] == 'admin':
            flash("Halaman ini tidak dapat diakses oleh admin", "danger")
            return redirect(url_for("indexAdmin"))

        user_info = db.users.find_one({"_id": ObjectId(payload["_id"])})
        if not user_info:
            flash("User tidak ditemukan", "danger")
            return redirect(url_for("showAuth"))
        
        form_info = db.form.find_one({"user_id": ObjectId(payload["_id"])})

        existing_doc = db.dokumen_santri.find_one({"user_id": user_info["_id"]})
        doc_submitted = bool(existing_doc)
        existing_form = db.form.find_one({"user_id": user_info["_id"]})
        form_submitted = bool(existing_form)

        if request.method == 'POST':
            file_fields = ['pas_foto', 'ijazah', 'surat_keterangan_lulus', 'akta_kelahiran', 'kartu_keluarga', 'surat_memiliki_nisn']
            file_paths = {}
            missing_files = [field for field in file_fields if field not in request.files or request.files[field].filename == '']

            if missing_files:
                flash(f'Dokumen berikut belum lengkap: {", ".join(missing_files)}', 'danger')
                return redirect(url_for('showdoc'))

            all_files_saved = True

            for field in file_fields:
                if field in request.files:
                    file = request.files[field]
                    if file.filename == '':
                        flash(f'Nama file tidak valid untuk {field}', 'danger')
                        all_files_saved = False
                        break

                    if not allowed_file(file.filename):
                        flash(f'Tipe file tidak diizinkan untuk {field}', 'danger')
                        all_files_saved = False
                        break

                    filename = f"{field}_{user_info['_id']}_{datetime.now().strftime('$%d%m%Y%H%M%S')}.jpg"
                    file_path = Path(app.config['UPLOAD_DOKUMEN']) / filename
                    try:
                        file.save(file_path)
                        file_paths[field] = f"/{file_path.as_posix()}"
                    except Exception as e:
                        flash(f'Error saat menyimpan file {filename}: {e}', 'danger')
                        all_files_saved = False
                        break

            if all_files_saved:
                try:
                    file_paths['user_id'] = user_info['_id']
                    file_paths['tanggal upload'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    db.dokumen_santri.insert_one(file_paths)
                    
                    db.users.update_one(
                        {"_id": user_info['_id']},
                        {"$set": {"status dokumen": "Pending", "tanggal upload dokumen": file_paths['tanggal upload']}}
                    )
                    flash('Dokumen berhasil diupload', 'success')
                except Exception as e:
                    flash(f'Error saat mengupload dokumen: {e}', 'danger')
                    return redirect(url_for('showdoc'))

            return redirect(url_for('showdoc'))

        return render_template("dashboard_user/dokumen.html", user_info=user_info, form_info=form_info, data=data, doc_submitted=doc_submitted, form_submitted=form_submitted, existing_doc=existing_doc)

    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

# DASHBOARD STATUS ROUTES
@app.route('/dashboard/status', methods=['GET', 'POST'])
def showVer():
    data = {
        'title': 'Status Pendaftaran',
    }
    token_receive = request.cookies.get("tokenLogin")
    if not token_receive:
        flash("Silahkan login terlebih dahulu", "danger")
        return redirect(url_for("showAuth"))
    
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' in payload and payload['role'] == 'admin':
            flash("Halaman ini tidak dapat diakses oleh admin", "danger")
            return redirect(url_for("indexAdmin"))
        
        user_info = db.users.find_one({"_id": ObjectId(payload["_id"])})
        if not user_info:
            flash("User tidak ditemukan", "danger")
            return redirect(url_for("showAuth"))

        
        data['status_formulir'] = user_info.get('status formulir', '')
        data['status_dokumen'] = user_info.get('status dokumen', '')
        data['status_pembayaran'] = user_info.get('status pembayaran', '')
        
        
        if user_info['status formulir'] == 'Pending':
            data['message_formulir'] = "Pendaftaran anda sedang diverifikasi"
        elif user_info['status formulir'] == 'Done':
            data['message_formulir'] = "Pendaftaran anda telah diterima"
        elif user_info['status formulir'] == 'Rejected':
            data['message_formulir'] = user_info.get('tolak_form')
        else:
            data['message_formulir'] = "Belum mengisi"

        if user_info['status dokumen'] == 'Pending':
            data['message_dokumen'] = "Dokumen anda sedang diverifikasi"
        elif user_info['status dokumen'] == 'Done':
            data['message_dokumen'] = "Dokumen anda telah diterima"
        elif user_info['status dokumen'] == 'Rejected':
            data['message_dokumen'] = user_info.get('tolak_doc')
        else:
            data['message_dokumen'] = "Belum mengisi"

        if user_info['status pembayaran'] == 'Pending':
            data['message_pembayaran'] = "Pembayaran anda sedang diverifikasi"
        elif user_info['status pembayaran'] == 'Done':
            data['message_pembayaran'] = "Pembayaran anda telah diterima"
        elif user_info['status pembayaran'] == 'Rejected':
            data['message_pembayaran'] = user_info.get('tolak_pay')
        else:
            data['message_pembayaran'] = "Belum mengisi"

        return render_template('dashboard_user/StatusPendaftaran.html', data=data, user_info=user_info)

    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

# DASHBOARD PEMBAYARAN ROUTES
@app.route('/dashboard/pembayaran', methods=['GET', 'POST'])
def showPembayaran():
    data = {
        'title': 'Pembayaran',
    }
    token_receive = request.cookies.get("tokenLogin")
    if not token_receive:
        flash("Silahkan login terlebih dahulu", "danger")
        return redirect(url_for("showAuth"))
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' in payload and payload['role'] == 'admin':
            flash("Halaman ini tidak dapat diakses oleh admin", "danger")
            return redirect(url_for("indexAdmin"))
        
        user_info = db.users.find_one({"_id": ObjectId(payload["_id"])})
        if not user_info:
            flash("User tidak ditemukan", "danger")
            return redirect(url_for("showAuth"))
        
        existing_pay = db.pembayaran.find_one({"user_id": user_info["_id"]})
        pay_submitted = bool(existing_pay)
        
        
        if request.method == 'POST':
            bukti = request.files.get('bukti')

            if not bukti or not allowed_file(bukti.filename):
                flash('Wajib upload bukti pembayaran dengan format yang benar (png, jpg, jpeg)', 'danger')
                return redirect(url_for('showPembayaran'))
            
            filename = f"pembayaran_{user_info['_id']}_{datetime.now().strftime('%d%m%Y%H%M%S')}.jpg"
            file_path = Path(app.config['UPLOAD_PEMBAYARAN']) / filename
            
            try:
                bukti.save(file_path)
            except Exception as e:
                flash(f'Error menyimpan file: {e}', 'danger')
                return redirect(url_for('showPembayaran'))

            try:
                doc = {
                    'user_id': user_info['_id'],
                    'foto bukti': f'/{file_path.as_posix()}'
                }
                doc['tanggal bayar'] = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                db.pembayaran.insert_one(doc)

                db.users.update_one(
                        {"_id": user_info['_id']},
                        {"$set": {"status pembayaran": "Pending", "tanggal bayar": doc['tanggal bayar']}}
                    )

                flash('Bukti pembayaran berhasil dikirim, menunggu verifikasi.', 'success')
            except Exception as e:
                flash(f'Error saat mengupload dokumen: {e}', 'danger')
                return redirect(url_for('showPembayaran'))

            return redirect(url_for('showPembayaran'))

        return render_template('dashboard_user/pembayaran.html', user_info=user_info, data=data, pay_submitted=pay_submitted)

    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("Token anda tidak valid, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

if __name__ == '__main__':
    app.run(debug=True)
