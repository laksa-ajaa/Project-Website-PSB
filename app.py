import os
from os.path import join, dirname
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request, url_for, redirect, flash, session, make_response
import jwt
import hashlib
from pymongo import MongoClient
from datetime import datetime, timedelta


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")
SECRET_KEY = os.environ.get("SECRET_KEY")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

app.secret_key = SECRET_KEY
 
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/dokumen"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    data = {
        'title': 'Login/Register',
    }
    return render_template('auth/login.html', data=data)

@app.route('/login', methods=['POST'])
def auth():
    email = request.form["email"]
    password = request.form["password"]
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    cek_login = db.users.find_one({"email": email, "password": password_hash})
    if cek_login:
        payload = {
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        response = make_response(redirect(url_for('showDashUser')))
        response.set_cookie("tokenLogin", token)
        return response
    else:
        return jsonify({"status": "error", "msg": "Email atau password salah"})

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
        "password": password_hash
    }
    db.users.insert_one(doc)
    return jsonify({"status": "success"})

@app.route('/')
def showHome():
    data = {
        'title': 'Beranda',
    }
    token_receive = request.cookies.get("tokenLogin")
    if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"email": payload["email"]})
            return render_template('user_page/index.html', data=data, user_info=user_info)
    else:
        return render_template('user_page/index.html', data=data)

@app.route('/sejarah')
def showSejarah():
    data = {
        "title": "Ulumul Qur'an | Sejarah",
    }
    token_receive = request.cookies.get("tokenLogin")
    if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"email": payload["email"]})
            return render_template('user_page/sejarah.html', data=data, user_info=user_info)
    else:
        return render_template('user_page/sejarah.html', data=data)

@app.route('/kontak')
def showKontak():
    data = {
        "title": "Ulumul Qur'an | Kontak",
    }
    token_receive = request.cookies.get("tokenLogin")
    if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"email": payload["email"]})
            return render_template('user_page/kontak.html', data=data, user_info=user_info)
    else:
        return render_template('user_page/kontak.html' , data=data)

@app.route('/visimisi')
def showVisiMisi():
    data = {
        "title": "Ulumul Qur'an | Visi & Misi",
    }
    token_receive = request.cookies.get("tokenLogin")
    if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"email": payload["email"]})
            return render_template('user_page/visimisi.html', data=data, user_info=user_info)
    else:
        return render_template('user_page/visimisi.html' , data=data)

@app.route('/kegiatan')
def showKegiatan():
    data = {
        "title": "Ulumul Qur'an | Kegiatan & Fasilitas",
    }
    token_receive = request.cookies.get("tokenLogin")
    if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"email": payload["email"]})
            return render_template('user_page/kegiatan.html', data=data, user_info=user_info)
    else:
        return render_template('user_page/kegiatan.html' , data=data)

@app.route('/template')
def showTemp():
    data = {
        'title': 'Template',
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]})
        return render_template("dashboard_user/index.html", user_info=user_info, data=data)
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
                    "username": username,
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
        
        admin_info = db.admin.find_one({"username": payload["username"], "role": payload["role"]})
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
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"username": payload["username"], "role": payload["role"]})
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
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    
@app.route('/admin/datapeserta')
def pesertaAdmin():
    data = {
        'title': 'Dashboard Admin',
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"username": payload["username"], "role": payload["role"]})
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
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
@app.route('/admin/verifikasipeserta')
def verifyAdmin():
    data = {
        'title': 'Dashboard Admin',
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"username": payload["username"], "role": payload["role"]})
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
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
@app.route('/admin/pembayaran')
def paymentAdmin():
    data = {
        'title': 'Dashboard Admin',
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'role' not in payload:
            flash("Halaman ini tidak dapat diakses, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response
        
        admin_info = db.admin.find_one({"username": payload["username"], "role": payload["role"]})
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
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response













# User Backend
@app.route('/dashboard')
def showDashUser():
    data = {
        'title': 'Dashboard User',
    }
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]})
        return render_template("dashboard_user/index.html", user_info=user_info, data=data)
    except jwt.ExpiredSignatureError:
        flash("Token anda sudah kadaluarsa, silahkan login kembali", "danger")
        response = make_response(redirect(url_for("authAdmin")))
        response.delete_cookie("tokenLogin")
        return response
    except jwt.exceptions.DecodeError:
        flash("silahkan login terlebih dahulu", "danger")
        response = make_response(redirect(url_for("showAuth")))
        response.delete_cookie("tokenLogin")
        return response

@app.route('/dashboard/formulir', methods=["GET"])
def showformulir():
    data = {}
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]})
        return render_template("dashboard_user/formulir.html", user_info=user_info, data=data)
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
@app.route('/dashboard/formulir', methods=["POST"])
def postformulir():
    if request.method=="POST":
        data = {
            "nama" : request.form["nama"],
            "tempat_lahir" : request.form["tempat_lahir"],
            "tanggal_lahir" : request.form["tanggal_lahir"],
            "jenis_kelamin" : request.form["jenis_kelamin"],
            "alamat" : request.form["alamat"],
            "sekolah_asal" : request.form["sekolah_asal"],
            "nisn" : request.form["nisn"],
            "anak_ke" : request.form["anak_ke"],
            "email" : request.form["email"],
            "pendidikan" : request.form["pendidikan"],
            "program" : request.form["program"],
            "motivasi" : request.form["motivasi"],
            "nama_ibu" : request.form["nama_ibu"],
            "nik_ibu" : request.form["nik_ibu"],
            "tempat_lahir_ibu" : request.form["tempat_lahir_ibu"],
            "tanggal_lahir_ibu" : request.form["tanggal_lahir_ibu"],
            "no_hp_ibu" : request.form["no_hp_ibu"],
            "nama_ayah" : request.form["nama_ayah"],
            "nik_ayah" : request.form["nik_ayah"],
            "tempat_lahir_ayah" : request.form["tempat_lahir_ayah"],
            "tanggal_lahir_ayah" : request.form["tanggal_lahir_ayah"],
            "no_hp_ayah" : request.form["no_hp_ayah"]
        }
        db.form.insert_one(data)
        return render_template('dashboard_user/formulir.html', data=data)

#<<<<<<< HEAD
@app.route('/dashboard/dokumen', methods=["GET", "POST"])
def showdoc():
    if request.method == 'POST':
        # Daftar file yang diunggah
        file_fields = [
            'pas_foto', 'ijazah_sd', 'ijazah_mts', 
            'surat_keterangan_lulus', 'akta_kelahiran', 
            'surat_memilik_nisn', 'surat_peryataan'
        ]
        
        # Menyimpan jalur file yang diunggah
        file_paths = {}

        for field in file_fields:
            if field in request.files:
                file = request.files[field]
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    try:
                        file.save(file_path)
                        file_paths[field] = file_path
                        flash(f'File {filename} berhasil diunggah', 'success')
                    except Exception as e:
                        flash(f'Error saat menyimpan file {filename}: {e}', 'danger')
                else:
                    flash(f'File {file.filename} tidak diizinkan', 'danger')

        # Simpan informasi jalur file ke MongoDB
        try:
            db.uploaded_files.insert_one(file_paths)
            flash('Semua file berhasil disimpan ke database', 'success')
        except Exception as e:
            flash(f'Error saat menyimpan data ke database: {e}', 'danger')
        
        if 'user_email' in session:
            user_email = session['user_email']
            try:
                db.pend_santri.update_one(
                    {"email": user_email},
                    {"$set": {"status": "Menunggu Verifikasi", **file_paths}},
                    upsert=True
                )
                flash('Semua file berhasil disimpan ke database dan status pendaftaran diubah ke Menunggu Verifikasi', 'success')
            except Exception as e:
                flash(f'Error saat menyimpan data ke database: {e}', 'danger')
        else:
            flash('Anda harus login terlebih dahulu untuk mengunggah dokumen', 'danger')

        return redirect(url_for('showdoc'))
#=======
@app.route('/dashboard/dokumen', methods=["GET"])
def showdoc():
    data = {}
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]})
        return render_template("dashboard_user/index.html", user_info=user_info, data=data)
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
@app.route('/dashboard/dokumen', methods=["POST"])
def postdoc():
#>>>>>>> 1706386eb7fd5654a166d9060a3616968d51b5df

    return render_template('dashboard_user/dokumen.html')

@app.route('/dashboard/status')
def showVer():
    if 'user_email' in session:
        user_email = session ['user_email']
        data = db.pend_santri.find_one({"email" : user_email})
        if data:
            status = data.get("status", "Menunggu Verifikasi")
            return render_template('dashboard_user/StatusPendaftaran.html', status=status )
        else:
            flash('Data Pendaftaran tidak ditemukan.', 'Silahkan Login')
            return redirect(url_for('showformulir'))
    else:
        return redirect(url_for('showformulir'))

@app.route('/dashboard/pembayaran', methods=['GET', 'POST'])
def showPembayaran():
    if request.method == 'POST':
        print(request.form)
        nama = request.form.get('nama')
        kelas = request.form.get('kelas')
        jumlah = request.form.get('jumlah')
        metode = request.form.get('metode')
        tanggal = request.form.get('tanggal')
        bukti = request.files.get('bukti')

        if not bukti or not allowed_file(bukti.filename):
            flash('Wajib upload bukti pembayaran dengan format yang benar (png, jpg, jpeg, gif)', 'danger')
            return redirect(url_for('showPembayaran'))
        
        filename = secure_filename(bukti.filename)
        bukti_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        try:
            bukti.save(bukti_path)
        except Exception as e:
            flash(f'Error menyimpan file: {e}', 'danger')
            return redirect(url_for('showPembayaran'))

        # Save to database
        doc = {
            'nama': nama,
            'kelas': kelas,
            'jumlah': jumlah,
            'metode': metode,
            'tanggal': tanggal,
            'bukti_path': bukti_path,
            "status": "Menunggu Verifikasi"
        }
        db.pembayaran.insert_one(doc)

        flash('Pembayaran berhasil dikirim, menunggu verifikasi.', 'success')
        return redirect(url_for('showPembayaran'))

    return render_template('dashboard_user/Pembayaran.html')


if __name__ == '__main__':
    app.run(debug=True)