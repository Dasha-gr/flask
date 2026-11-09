import pymysql
from flask import Flask, render_template, request, session, redirect, url_for

db = pymysql.connect(
    host="localhost",
    user="root",
    password="1111",
    database="flask",
    charset="utf8mb4"
)
print(db)


app = Flask(__name__)
app.secret_key = 'super_secret_key_123'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    with db.cursor() as cur:
        cur.execute("SELECT id, title, description, price FROM myproj_service ORDER BY id DESC")
        items = cur.fetchall()
    return render_template('services.html', items=items)
@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if name and email and message:
            with db.cursor() as cur:
                # Сохраняем в базу
                cur.execute(
                    "INSERT INTO myproj_message (name, email, subject, message) VALUES (%s, %s, %s, %s)",
                    (name, email, subject, message)
                )
                db.commit()  # Сохраняем
            return render_template('contact.html', success=True)

        return render_template('contact.html', error="Заполните обязательные поля")

    return render_template('contact.html')

# --- ВХОД ---
@app.route('/admin', methods=['GET', 'POST'])
def dosup():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        with db.cursor() as cur:
            cur.execute("SELECT id, login FROM myproj_admin WHERE login=%s AND password=%s", (login, password))
            user = cur.fetchone()

        if user:
            session['admin_logged_in'] = True
            session['admin_name'] = user[1]
            return redirect(url_for('admin_panel'))

        return render_template('login.html', error="Неверный логин или пароль")

    return render_template('login.html')


# --- ПАНЕЛЬ И ДОБАВЛЕНИЕ УСЛУГ ---
@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('dosup'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')

        with db.cursor() as cur:
            # Вносим данные в бд с помощью INSERT
            cur.execute(
                "INSERT INTO myproj_service (title, description, price) VALUES (%s, %s, %s)",
                (title, description, price)
            )
        db.commit()
        return redirect(url_for('admin_panel'))

    with db.cursor() as cur:
        # Вытаскиваем данные из бд с помощью SELECT
        cur.execute("SELECT id, title, description, price FROM myproj_service ORDER BY id DESC")
        items = cur.fetchall()

    return render_template('admin.html', items=items)


@app.route('/logout')
def logout():
    session.clear() #Стираем данные о заходе
    return redirect(url_for('dosup'))


if __name__ == '__main__':
    app.run(debug=True)