from flask import Flask, render_template

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

@app.route('/formulir')
def showformulir():
    return render_template('dashboard_user/Formulir.html')

@app.route('/DashboardUser')
def showDashUser():
    return render_template('dashboard_user/Dashboard-user.html')

@app.route('/Verifikasi')
def showVer():
    return render_template('dashboard_user/Verifikasi.html')

@app.route('/Pembayaran')
def showPembayaran():
    return render_template('dashboard_user/Pembayaran.html')

if __name__ == '__main__':
    app.run(debug=True)
