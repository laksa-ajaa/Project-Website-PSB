from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def showHome():
    return render_template('user_page/index.html')

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
    return render_template('dashboard_user/template.html')

if __name__ == '__main__':
    app.run(debug=True)
