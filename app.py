from flask import Flask, redirect, url_for, render_template, request, jsonify, send_from_directory, send_file, make_response


app = Flask(__name__)

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
    return render_template('dashboard_admin/table.html')
@app.route('/admin/verifikasipeserta')
def verifyAdmin():
    return render_template('dashboard_admin/widget.html')
@app.route('/admin/pembayaran')
def paymentAdmin():
    return render_template('dashboard_admin/form.html')

@app.route('/formulir', methods=["GET", "POST"])
def showformulir():
    if request.method=="POST":
        data = {
            "nama" : request.form["nama"],
            "tempat_lahir" : request.form["tempat_lahir"],
            "tanggal_lahir" : request.form["tanggal_lahir"],
            "alamat" : request.form["alamat"],
            "no_hp" : request.form["no_hp"],
            "email" : request.form["email"],
            "pendidikan" : request.form["pendidikan"],
            "program" : request.form["program"],
            "motivasi" : request.form["motivasi"]
        }
        db.pend_santri.insert_one[data]
    return render_template('dashboard_user/Formulir.html' , data=data)

@app.route('/DashboardUser')
def showDashUser():
    data = {
        'title': 'Template',
    }
    return render_template('dashboard_user/Dashboard-user.html', data=data)

@app.route('/Verifikasi')
def showVer():
    data = {
        'title': 'Template',
    }
    return render_template('dashboard_user/Verifikasi.html' , data=data)

@app.route('/Pembayaran')
def showPembayaran():
    data = {
        'title': 'Template',
    }
    return render_template('dashboard_user/Pembayaran.html' , data=data)

if __name__ == '__main__':
    app.run(debug=True)
