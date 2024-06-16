import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, url_for, redirect, flash, session
from werkzeug.utils import secure_filename
import jwt
import hashlib
from pymongo import MongoClient
from datetime import datetime, timedelta
import re

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

app = Flask(__name__)
SECRET_KEY = "users"

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)
app.secret_key = "users"

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/dokumen"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def showHome():
    data = {
        'title': 'Beranda',
    }
    return render_template('user_page/index.html', data=data)

@app.route('/auth')
def showAuth():
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
    cek_login = db.dbsantri.find_one({"email": email, "password": password_hash})
    if cek_login:
        payload = {
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify({"status": "success", "token": token})
    else:
        return jsonify({"status": "error", "msg": "Email atau password salah"})

@app.route('/register', methods = ["post"])
def register():
    nama = request.form["nama"]
    email = request.form["email"]
    phone = request.form["phone"]
    password = request.form["password"]
    repassword = request.form["repassword"]
    
    # Validasi input dasar
    if not nama or not email or not phone or not password or not repassword:
        return jsonify({"status": "error", "message": "Semua field harus diisi"})
    
    # Validasi format email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"status": "error", "message": "Format email tidak valid"})
    
    # Validasi kesesuaian password
    if password != repassword:
        return jsonify({"status": "error", "message": "Password dan konfirmasi password tidak cocok"})
    
    # Periksa apakah email sudah terdaftar
    cek_email = db.dbsantri.find_one({"email": email})
    if cek_email:
        return jsonify({"status": "error", "message": "Email sudah terdaftar"})
    
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    doc = {
        "nama": nama,
        "email": email,
        "phone": phone,
        "password": password_hash
    }
    db.dbsantri.insert_one(doc)
    return jsonify({"status": "success"})



@app.route('/sejarah')
def showSejarah():
    return render_template('user_page/sejarah.html')

@app.route('/kontak')
def showKontak():
    return render_template('user_page/kontak.html')

@app.route('/visimisi')
def showVisiMisi():
    
    return render_template('user_page/visimisi.html')

@app.route('/kegiatan')
def showKegiatan():
    return render_template('user_page/kegiatan.html')

@app.route('/template')
def showTemp():
    data = {
        'title': 'Template',
    }
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.dbsantri.find_one({"email": payload["email"]})
        return render_template("dashboard_user/index.html", user_info=user_info, data=data)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("showAuth", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("showAuth", msg="There was problem logging you in"))
    
#Routes Login Admin
@app.route('/authAdmin')
def showAuthadmin():
    data = {
        'title': 'Login',
    }
    return render_template('auth/login_admin.html', data=data)

@app.route('/loginAdmin', methods=['POST'])
def authAdmin():
    email = request.form["email"]
    password = request.form["password"]
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Perhatikan: Di sini Anda harus memeriksa dengan password_hash, bukan password biasa
    cek_login = db.dbAdmin.find_one({"email": email, "password": password_hash})
    if cek_login:
        payload = {
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify({"status": "success", "token": token})
    else:
        return jsonify({"status": "error", "msg": "Email atau password salah"})
    
@app.route('/templateAdmin')
def showTempAdmin():
    data = {
        'title': 'TemplateAdmin',
    }
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        admin_info = db.dbAdmin.find_one({"email": payload["email"]})
        return render_template("dashboard_admin/index.html", admin_info=admin_info, data=data)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("showAuthAdmin", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("showAuthAdmin", msg="There was problem logging you in"))

# Routes Dashboard Admin
@app.route('/admin')
def indexAdmin():
    return render_template('dashboard_admin/index.html')
@app.route('/admin/datapeserta')
def pesertaAdmin():
    return render_template('dashboard_admin/dataPeserta.html')
@app.route('/admin/verifikasipeserta')
def verifyAdmin():
    return render_template('dashboard_admin/widget.html')
@app.route('/admin/pembayaran')
def paymentAdmin():
    return render_template('dashboard_admin/form.html')


# Routes Dashboard User
@app.route('/dashboard')
def showDashUser():
    data = {
        'title': 'Template',
    }
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.dbsantri.find_one({"email": payload["email"]})
        return render_template("dashboard_user/index.html", user_info=user_info, data=data)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("showAuth", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("showAuth", msg="There was problem logging you in"))

@app.route('/dashboard/formulir', methods=["GET", "POST"])
def showformulir():
    data = {}
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
        db.PS_baru.insert_one(data)
        return render_template('dashboard_user/Formulir.html', data=data)
    return render_template('dashboard_user/Formulir.html', data=data)

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