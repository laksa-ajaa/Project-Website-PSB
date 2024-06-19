import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, url_for, redirect, flash, session, make_response
from werkzeug.utils import secure_filename
import jwt
from bson.objectid import ObjectId
import hashlib
from pymongo import MongoClient
from datetime import datetime, timedelta

# Memuat variabel lingkungan dari file .env
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")
SECRET_KEY = os.environ.get("SECRET_KEY")  # Mengambil secret key dari file .env

if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Menetapkan secret key untuk aplikasi Flask

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

    # Perhatikan: Di sini Anda harus memeriksa dengan password_hash, bukan password biasa
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
    
    # Periksa apakah email sudah terdaftar
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
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if 'email' not in payload:
            flash("Token tidak valid, silahkan login kembali", "danger")
            response = make_response(redirect(url_for("showAuth")))
            response.delete_cookie("tokenLogin")
            return response

        # Pastikan kunci 'email' ada dalam payload sebelum mengaksesnya
        user_email = payload["email"]
        user_info = db.users.find_one({"email": user_email})
        if user_info:
            # Lakukan sesuatu dengan user_info
            return render_template("home.html", user_info=user_info)
        else:
            flash("Informasi pengguna tidak ditemukan", "danger")
            return redirect(url_for("showAuth"))
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
            pending_students = list(db.users.find({}))
            
            # Debugging
            print("Pending students:", pending_students)
            
            return render_template("dashboard_admin/index.html", admin_info=admin_info, data=data, pending_students=pending_students)
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
            return render_template("dashboard_admin/dataPeserta.html", admin_info=admin_info, data=data)
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
    
@app.route('/admin/verifikasipeserta', methods=['GET', 'POST'])
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
        if payload["role"] != "admin":
            flash("Anda tidak memiliki izin untuk mengakses halaman ini", "danger")
            response = make_response(redirect(url_for("authAdmin")))
            response.delete_cookie("tokenLogin")
            return response
        
        # Mendapatkan data siswa yang sedang menunggu verifikasi
        pending_students = list(db.users.find({}))
        
        # Debugging
        print("Pending students:", pending_students)

        if request.method == 'POST':
            student_id = request.form.get('student_id')
            action = request.form.get('action')

            if action == 'approve':
                db.users.update_one({"_id": ObjectId(student_id)}, {"$set": {"status": "verified"}})
                flash("Siswa berhasil diverifikasi", "success")
            elif action == 'reject':
                db.users.update_one({"_id": ObjectId(student_id)}, {"$set": {"status": "rejected"}})
                flash("Verifikasi siswa ditolak", "warning")

        return render_template("dashboard_admin/verifikasi.html", admin_info=admin_info, data=data, pending_students=pending_students)
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

@app.route('/admin/pembayaran', methods=['GET', 'POST'])
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
            if request.method == 'POST':
                student_id = request.form.get('student_id')
                action = request.form.get('action')
                
                if action == 'approve':
                    db.pembayaran.update_one({'_id': ObjectId(student_id)}, {'$set': {'status': 'Approved'}})
                    flash("Pembayaran telah disetujui", "success")
                elif action == 'reject':
                    db.pembayaran.update_one({'_id': ObjectId(student_id)}, {'$set': {'status': 'Rejected'}})
                    flash("Pembayaran telah ditolak", "danger")
                return redirect(url_for('paymentAdmin'))
            
            pembayaran_siswa = list(db.pembayaran.find({}))
            return render_template("dashboard_admin/pembayaran.html", admin_info=admin_info, data=data, pembayaran_siswa=pembayaran_siswa)
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

# Untuk menampilkan formulir
@app.route('/dashboard/formulir', methods=["GET"])
def showformulir():
    return render_template('dashboard_user/formulir.html', data=None)

# Untuk memproses formulir yang dikirim

from datetime import datetime

@app.route('/dashboard/formulir', methods=["POST"])
def postformulir():
    if request.method == "POST":
        data = {
            "nama": request.form["nama"],
            "tempat_lahir": request.form["tempat_lahir"],
            "tanggal_lahir": request.form["tanggal_lahir"],
            "jenis_kelamin": request.form["jenis_kelamin"],
            "alamat": request.form["alamat"],
            "sekolah_asal": request.form["sekolah_asal"],
            "nisn": request.form["nisn"],
            "anak_ke": request.form["anak_ke"],
            "email": request.form["email"],
            "pendidikan": request.form["pendidikan"],
            "program": request.form["program"],
            "motivasi": request.form["motivasi"],
            "nama_ibu": request.form["nama_ibu"],
            "nik_ibu": request.form["nik_ibu"],
            "tempat_lahir_ibu": request.form["tempat_lahir_ibu"],
            "tanggal_lahir_ibu": request.form["tanggal_lahir_ibu"],
            "no_hp_ibu": request.form["no_hp_ibu"],
            "nama_ayah": request.form["nama_ayah"],
            "nik_ayah": request.form["nik_ayah"],
            "tempat_lahir_ayah": request.form["tempat_lahir_ayah"],
            "tanggal_lahir_ayah": request.form["tanggal_lahir_ayah"],
            "no_hp_ayah": request.form["no_hp_ayah"],
            "tanggal_pendaftaran": datetime.now().strftime("%Y-%m-%d")  # Menggunakan tanggal saat ini
        }

        token_receive = request.cookies.get("tokenLogin")
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"email": payload["email"]})

            # Cek apakah status formulir sudah diisi sebelumnya
            if user_info.get("status_formulir") != "formulir sudah di isi":
                # Menyimpan data ke database
                db.form.insert_one(data)

                # Memperbarui status dan informasi pengguna di database
                db.users.update_one(
                    {"email": user_info['email']},
                    {
                        "$set": {
                            "status_formulir": "formulir sudah di isi",
                            "status": "pending",  # Set status to pending
                            "nama": data["nama"],
                            "tanggal_pendaftaran": data["tanggal_pendaftaran"]
                        }
                    }
                )

            # Mengarahkan pengguna ke halaman status setelah formulir diisi
            return redirect(url_for('showVer'))

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
    
    return render_template('dashboard_user/formulir.html', data=None)





#<<<<<<< HEAD
@app.route('/dashboard/dokumen', methods=["GET", "POST"])
def showdoc():
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, app.config['SECRET_KEY'], algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]})

        if request.method == 'POST':
            file_fields = ['pas_foto', 'ijazah_sd', 'ijazah_mts', 'surat_keterangan_lulus', 'akta_kelahiran', 'surat_memiliki_nisn', 'surat_peryataan']
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

            try:
                db_status = "Dokumen sudah diisi" if len(file_paths) == len(file_fields) else "Dokumen belum lengkap"
                status_verifikasi = "Pending" if db_status == "Dokumen sudah diisi" else "Belum diverifikasi"
                file_paths['status_dokumen'] = db_status
                file_paths['status_verifikasi'] = status_verifikasi
                
                db.uploaded_documen.insert_one(file_paths)  # Simpan file ke koleksi dokumen
                
                # Update status perubahan hanya di users
                db.users.update_one(
                    {"email": user_info['email']},
                    {"$set": {"status_dokumen": status_verifikasi, "status_verifikasi": db_status}},
                    upsert=True
                )
                
                flash('Semua file berhasil disimpan ke database dan status pendaftaran diubah', 'success')
            except Exception as e:
                flash(f'Error saat menyimpan data ke database: {e}', 'danger')

            return redirect(url_for('showdoc'))

        return render_template("dashboard_user/dokumen.html", user_info=user_info)
    
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

    return render_template('dashboard_user/dokumen.html')




@app.route('/dashboard/status', methods=['GET', 'POST'])
def showVer():
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]})

        if request.method == 'POST':
            statusformulir = request.form.get('status')  # Pastikan nama elemen formulir sesuai
            statusdoc = request.form.get('status_dokumen')  # Pastikan nama elemen formulir sesuai
            statuspembayaran = request.form.get('status_pembayaran')  # Pastikan nama elemen formulir sesuai

            if statusformulir == 'formulir sudah di isi':
                db.users.update_one(
                    {"email": user_info['email']},
                    {"$set": {"status_formulir": 'formulir sudah di isi'}}
                )

            if statusformulir == 'formulir sudah di isi' and statusdoc != 'dokumen sudah di isi':
                db.users.update_one(
                    {"email": user_info['email']},
                    {"$set": {"status_dokumen": 'dokumen belum di isi'}}
                )

            if statusdoc == 'dokumen sudah di isi' and statuspembayaran != 'pembayaran sudah di isi':
                db.users.update_one(
                    {"email": user_info['email']},
                    {"$set": {"status_pembayaran": 'belum di bayar'}}
                )

        data = {
            'nama': user_info.get('nama', ''),
            'tanggal_pendaftaran': user_info.get('tanggal_pendaftaran', ''),
            'catatan': 'Pendaftaran berhasil',
            'statusformulir': user_info.get('status_formulir', ''),
            'statusdoc': user_info.get('status_dokumen', ''),
            'statuspembayaran': user_info.get('status_pembayaran', '')
        }

        return render_template('dashboard_user/StatusPendaftaran.html', data=data)

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



    
@app.route('/dashboard/pembayaran', methods=['GET', 'POST'])
def showPembayaran():
    token_receive = request.cookies.get("tokenLogin")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["email"]})
        
        if request.method == 'POST':
            nama = request.form.get('nama')
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
                'jumlah': jumlah,
                'metode': metode,
                'tanggal': tanggal,
                'bukti_path': bukti_path,
                'status': 'Menunggu Verifikasi',
                'user_email': user_info['email']
            }
            db.pembayaran.insert_one(doc)

            # Update user status
            db.users.update_one(
                {"email": user_info['email']},
                {"$set": {"status_pembayaran": "pending"}}
            )

            flash('Pembayaran berhasil dikirim, menunggu verifikasi.', 'success')
            return redirect(url_for('showPembayaran'))

        return render_template('dashboard_user/Pembayaran.html', user_info=user_info)

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



if __name__ == '__main__':
    app.run(debug=True)