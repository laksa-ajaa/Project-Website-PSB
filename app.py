from flask import Flask, redirect, url_for, render_template, request, jsonify, send_from_directory, send_file, make_response

app = Flask(__name__)
SECRET_KEY = "users"


# Konfigurasi MongoDB

# Konfigurasi folder upload
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Konfigurasi Flask-Session
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def showHome():
    data = {
        'title': 'Beranda',
    }
    return render_template('user_page/index.html', data=data)

@app.route('/login')
def auth():
    data = {
        'title': 'Login/Register',
    }
    return render_template('auth/login.html', data=data)

#route login admin
@app.route('/loginAdmin')
def login_admin():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    result = db.admin.find_one({"email": email, "password": pw_hash})

    if result:
        payload = {
            "email": email,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        response = make_response(
            jsonify({
                "message": "success",
                "email": email,
                "token": token
            })
        )
        response.set_cookie("token", token)
        return response

    else:
        return jsonify({
            "message": "fail",
            "error": "We could not find a user with that email/password combination"
        })
    
def adminTokenAuth(view_func):
    @wraps(view_func)
    def decorator(*args, **kwargs):
        token_receive = request.cookies.get("token")
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            email = payload.get('email')
            admin_info = db.pend_santri.admin.find_one({'email': email})
            if admin_info:
                admin = [admin_info]
                return view_func(*args, admin=admin, **kwargs)
            else:
                return redirect(url_for('indexAdmin'))
        except jwt.ExpiredSignatureError:
            msg = 'Your token has expired'
            return redirect(url_for('indexAdmin', msg=msg))
        except jwt.exceptions.DecodeError:
            print("Received token:", token_receive)
            msg = 'There was a problem logging you in'
            return redirect(url_for('indexAdmin', msg=msg))

    return decorator

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
    return render_template('dashboard_user/template.html' , data=data)


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

#<<<<<<< HEAD
# Routes Dashboard Admin
#=======
#>>>>>> 91541897c9ff4eb5d061c97cd43e269572d0cbbc
@app.route('/DashboardUser')
def showDashUser():
    data = {
        'title': 'Template',
    }
    return render_template('dashboard_user/Dashboard-user.html', data=data)

@app.route('/formulir', methods=["GET", "POST"])
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

@app.route('/documen', methods=["GET","POST"])
def showdoc():

    return render_template('dashboard_user/dokumen.html')
@app.route('/StatusPendaftaran')
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

@app.route('/Pembayaran', methods=['GET', 'POST'])
def showPembayaran():
    if request.method == 'POST':
        print(request.form)
        nama = request.form.get('nama')
        kelas = request.form.get('kelas')
        jumlah = request.form.get('jumlah')
        metode = request.form.get('metode')
        tanggal = request.form.get('tanggal')
        bukti = request.files.get('bukti')

        if not bukti:
            flash('wajib upload bukti pembayaran', 'danger')
            return redirect(url_for('showPembayaran'))
        
        bukti_filename = bukti.filename
        bukti_path = os.path.join(UPLOAD_FOLDER, bukti_filename)
        bukti.save(bukti_path)

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

        flash('pembayaran berhasil dikirim, menunggu verifikasi.', 'success')
        return redirect(url_for('showPembayaran'))

    return render_template('dashboard_user/Pembayaran.html')


if __name__ == '__main__':
    app.run(debug=True)
