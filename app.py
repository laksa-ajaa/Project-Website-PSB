import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, url_for, redirect, flash, session, make_response
import jwt
from bson.objectid import ObjectId
import hashlib
from pymongo import MongoClient
from datetime import datetime, timedelta
from pathlib import Path

# Memuat variabel lingkungan dari file .env
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
    email = request.form["email"]
    password = request.form["password"]
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
    nama = request.form["nama"]
    email = request.form["email"]
    phone = request.form["phone"]
    password = request.form["password"]
    
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
        "status pembayaran": "None"
    }
    db.users.insert_one(doc)
    return jsonify({"status": "success"})

@app.route('/logout')
def logout():
    flash("Anda telah logout", "success")
    response = make_response(redirect(url_for('showAuth')))
    response.delete_cookie("tokenLogin")
    return response



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
            return render_template('user_page/index.html', data=data, user_info=user_info, admin_info=admin_info)
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
            return render_template('user_page/index.html', data=data, user_info=user_info, admin_info=admin_info)
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
            return render_template('user_page/index.html', data=data, user_info=user_info, admin_info=admin_info)
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
            return render_template('user_page/index.html', data=data, user_info=user_info, admin_info=admin_info)
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            response = make_response(redirect(url_for('showHome')))
            response.delete_cookie("tokenLogin")
            return response
    else:
        return render_template('user_page/kegiatan.html' , data=data)


#Admin Backend
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
    
@app.route('/templateAdmin')
def showTempAdmin():
    data = {
        'title': 'TemplateAdmin',
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

# Routes Dashboard Admin
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
            data['pendaftar'] = list(db.users.find({}))
            data['form'] = list(db.form.find({}))
            data['doc'] = list(db.doc.find({}))
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
            data['pendaftar'] = list(db.users.find({}))
            
            return render_template("dashboard_admin/pendaftar.html", admin_info=admin_info, data=data)
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

#VERIFIKASI FORMULIR
@app.route('/admin/formulir/aliyah', methods=['GET'])
def verifyFormulirMA():
    data = {
        'title': 'Dashboard Admin',
        'active': 'verifikasi'
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
        user_form = list(db.form.find({}))
        user_id = user_form[0]['user_id']
        user_info = db.users.find_one({"_id": ObjectId(user_id)})
                
        return render_template("dashboard_admin/formulir_ma.html", admin_info=admin_info, user_info=user_info, data=data, user_form=user_form)

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
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status formulir': 'Done'}})
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

@app.route('/admin/formulir/santri/<id>')
def detailFormulir(id):
    data = {
        'title': 'Detail Formulir',
        'active': 'verifikasi'
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
        return render_template("dashboard_admin/form_detail.html", data=data, user_form=user_form , admin_info=admin_info)
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

#VERIFIKASI DOKUMEN
@app.route('/admin/dokumen/aliyah', methods=['GET'])
def verifyDokumenMA():
    data = {
        'title': 'Dashboard Admin',
        'active': 'verifikasi'
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
        
        user_form = list(db.form.find({}))
        user_id = user_form[0]['user_id']
        user_info = db.users.find_one({"_id": ObjectId(user_id)})
        
        return render_template("dashboard_admin/dokumen_ma.html", data=data, admin_info=admin_info , user_info=user_info, user_form=user_form)
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
        'active': 'verifikasi'
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
        return render_template("dashboard_admin/doc_detail_ma.html", data=data, user_doc=user_doc , admin_info=admin_info)
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
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status dokumen': 'Done'}})
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



#VERIFIKASI PEMBAYARAN 
@app.route('/admin/pembayaran/aliyah', methods=['GET'])
def verifyPembayaranMA():
    data = {
        'title': 'Dashboard Admin',
        'active': 'verifikasi'
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
        
        user_form = list(db.form.find({}))
        user_id = user_form[0]['user_id']
        user_info = db.users.find_one({"_id": ObjectId(user_id)})
        
        return render_template("dashboard_admin/pembayaran_ma.html", data=data, admin_info=admin_info , user_info=user_info, user_form=user_form)
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
        'active': 'verifikasi'
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
        return render_template("dashboard_admin/pay_detail_ma.html", data=data, user_pay=user_pay , admin_info=admin_info)
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
        db.users.update_one({'_id': ObjectId(id)}, {'$set': {'status pembayaran': 'Done'}})
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



# User Backend
@app.route('/dashboard')
def showDashUser():
    data = {
        'title': 'Dashboard User',
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



# Untuk menampilkan formulir
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
                "nama": request.form["nama"],
                "tempat lahir": request.form["tempat_lahir"],
                "tanggal lahir": request.form["tanggal_lahir"],
                "jenis kelamin": request.form["jenis_kelamin"],
                "alamat": request.form["alamat"],
                "NISN": request.form["nisn"],
                "sekolah asal": request.form["sekolah_asal"],
                "pendidikan": request.form["pendidikan"],
                "program": request.form["program"],
                "nama ibu": request.form["nama_ibu"],
                "nik ibu": request.form["nik_ibu"],
                "tempat lahir ibu": request.form["tempat_lahir_ibu"],
                "tanggal lahir ibu": request.form["tanggal_lahir_ibu"],
                "no telepon ibu": request.form["no_hp_ibu"],
                "nama ayah": request.form["nama_ayah"],
                "nik ayah": request.form["nik_ayah"],
                "tempat lahir ayah": request.form["tempat_lahir_ayah"],
                "tanggal lahir ayah": request.form["tanggal_lahir_ayah"],
                "no telepon ayah": request.form["no_hp_ayah"],
                "tanggal pendaftaran": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }

            db.form.insert_one(data)

            db.users.update_one(
                {"_id": ObjectId(user_info["_id"])},
                {
                    "$set": {
                        "status formulir": "Pending",
                        "nama": data["nama"],
                        "tanggal pendaftaran": data["tanggal pendaftaran"]
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

                    filename = f"{user_info['_id']}_{field}.jpg"
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

        data = {
            'status_formulir': user_info.get('status formulir', ''),
            'status_dokumen': user_info.get('status dokumen', ''),
            'status_pembayaran': user_info.get('status pembayaran', ''),
        }
        
        if user_info['status formulir'] == 'Pending':
            data['message_formulir'] = "Pendaftaran anda sedang diverifikasi"
        elif user_info['status formulir'] == 'Done':
            data['message_formulir'] = "Pendaftaran anda telah diterima"
        else:
            data['message_formulir'] = "Belum mengisi"

        if user_info['status dokumen'] == 'Pending':
            data['message_dokumen'] = "Dokumen anda sedang diverifikasi"
        elif user_info['status dokumen'] == 'Done':
            data['message_dokumen'] = "Dokumen anda telah diterima"
        else:
            data['message_dokumen'] = "Belum mengisi"

        if user_info['status pembayaran'] == 'Pending':
            data['message_pembayaran'] = "Pembayaran anda sedang diverifikasi"
        elif user_info['status pembayaran'] == 'Done':
            data['message_pembayaran'] = "Pembayaran anda telah diterima"
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
            
            filename = f"pembayaran_{user_info['_id']}.jpg"
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

        return render_template('dashboard_user/Pembayaran.html', user_info=user_info, data=data, pay_submitted=pay_submitted)

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