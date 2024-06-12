from flask import Flask, render_template, jsonify, request, url_for
import jwt
import hashlib
from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient("mongodb+srv://laksmanachairutama:lcacanony123@cluster0.zddwrtt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.dbsantri
app = Flask(__name__)
SECRET_KEY = "users"


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
    return render_template('dashboard_admin/dataPeserta.html')
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
    return render_template('dashboard_user/Formulir.html')

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
