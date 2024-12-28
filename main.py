import sqlite3
from cachelib import FileSystemCache
from flask import Flask, render_template, request, flash, session, redirect, url_for
from flask_session import Session
from datetime import timedelta
con = sqlite3.connect('1bd.db', check_same_thread=False)
cursor = con.cursor()
app = Flask(__name__)
app.secret_key = '12345'
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='flask_session', threshold=500)
Session(app)
@app.route('/')
def page_index():
    cursor.execute("SELECT * FROM post")
    a = cursor.fetchall()
    cursor.execute("SELECT * FROM users")
    c = cursor.fetchall()
    return render_template('index.html', a=a, c=c)

@app.route('/add_post/')
def add_post():
    if 'login' not in session:
        flash('Необходимо авторизоваться', 'danger')
        return redirect(url_for('registration'))
    return render_template('add.html')

@app.route('/upload/', methods=['POST'])
def save_post():
    image = request.files.getlist('image')
    for i in image:
        title = request.form['title']
        description = request.form['description']
        a = f'/uploads/{i.filename}'
        i.save(a)
        cursor.execute(
            "INSERT INTO post (title, file_name, discription) VALUES (?,?,?)",
            [title, a, description])
        con.commit()
    return redirect(url_for('page_index'))

@app.route('/registr/')
def registration():
    return render_template('registr.html')

@app.route('/save_register/', methods=['POST', 'GET'])
def save_inf():
    if request.method == 'POST':
        last_name = request.form['last_name']
        name = request.form['name']
        patronymic = request.form['patronymic']
        gender = request.form['gender']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        cursor.execute("INSERT INTO users (last_name, name, patronymic, gender, email, username, password) VALUES (?,?,?,?,?,?,?)",[last_name, name, patronymic, gender, email, username, password])
        con.commit()
    return redirect(url_for('add_reg'))

@app.route('/login/')
def add_reg():
    return render_template('autar.html')

@app.route('/authorization/',methods=['POST', 'GET'])
def aut_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM users WHERE username = (?)', [username])
        data = cursor.fetchall()[0]
        print(data)
        if data:
            if password == data[-1]:
                flash('Вы авторизованы', 'success')
                session['login'] = True
                session['username'] = username
                session.permanent = False
                app.permanent_session_lifetime = timedelta(minutes=1)
                session.modified = True
                return redirect(url_for('page_index'))
            else:
                flash('Неверный логин или пороль', 'danger')
                return redirect(url_for('registration'))
            return redirect(url_for('page_index'))

@app.route('/detail/<i>')
def post(i):
    cursor.execute('SELECT * FROM post WHERE id = (?)', [i])
    b = cursor.fetchall()
    return render_template('detail.html', b=b)

@app.route('/find/', methods=['POST', 'GET'])
def fnd_user():
    if request.method == 'POST':
        print(32423)
        id = request.form['id']
        cursor.execute('SELECT * FROM users WHERE id = (?)', [id])
        c = cursor.fetchall()
        cursor.execute('SELECT file_name FROM post WHERE id = (?)', [id])
        d = cursor.fetchall()
        if c:
            cursor.execute('SELECT flag FROM users')
            e = cursor.fetchall()
            cursor.execute('SELECT podpis FROM users')
            f = cursor.fetchall()
            if e == False:
                f+=1
                cursor.execute(
                    "INSERT INTO user (podpis) VALUES (?)",
                    [f])
                con.commit()
                e = True
            elif e == True:
                f -= 1
                cursor.execute(
                    "INSERT INTO user (podpis) VALUES (?)",
                    [f])
                con.commit()
                e = False
            return render_template('result_id.html', c=c, d=d)
        else:
            return redirect(url_for('page_index'))
    return render_template('result_id.html')

@app.route("/logout")
def logout():
    session.clear()
    flash('Вы вышли из профиля', 'danger')
    return redirect(url_for('page_index'))

app.run(debug=True)