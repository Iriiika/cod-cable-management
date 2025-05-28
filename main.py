from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg
import bcrypt

# Создание приложения Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Секретный ключ для сессий

# Настройки базы данных PostgreSQL
DB_CONFIG = {
    'dbname': 'cod_db',
    'user': 'postgres',
    'password': 'password123',
    'host': 'localhost',
    'port': '5432'
}

# Функция подключения к базе
def get_db_connection():
    try:
        conn = psycopg.connect(**DB_CONFIG)
        return conn
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        return None

# Страница авторизации
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['username']
        password = request.form['password'].encode('utf-8')

        conn = get_db_connection()
        if conn is None:
            return render_template('login.html', error='Ошибка сервера')

        try:
            with conn.cursor() as cur:
                cur.execute('SELECT id, full_name, role, password FROM users WHERE login = %s', (login,))
                user = cur.fetchone()

            if user and bcrypt.checkpw(password, user[3].encode('utf-8')):
                session['user_id'] = user[0]
                session['full_name'] = user[1]
                session['role'] = user[2]

                if user[2] == 'Администратор':
                    return redirect(url_for('admin_dashboard'))
                elif user[2] == 'Инженер ЛВС':
                    return redirect(url_for('engineer_dashboard'))
                else:
                    return redirect(url_for('observer_dashboard'))
            else:
                return render_template('login.html', error='Запросите доступ у <a href="mailto:SergeyAIvanov@dom.ru">SergeyAIvanov@dom.ru</a>')
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()

    return render_template('login.html')

# Дашборд администратора
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'Администратор':
        return redirect(url_for('login'))
    return render_template('main_admin.html', full_name=session['full_name'])

# Дашборд инженера ЛВС
@app.route('/engineer')
def engineer_dashboard():
    if 'user_id' not in session or session['role'] != 'Инженер ЛВС':
        return redirect(url_for('login'))
    return render_template('main_engineer.html', full_name=session['full_name'])

# Дашборд наблюдателя
@app.route('/observer')
def observer_dashboard():
    if 'user_id' not in session or session['role'] != 'Наблюдатель':
        return redirect(url_for('login'))
    return render_template('main_observer.html', full_name=session['full_name'])

# Страница коммутации
@app.route('/commutation')
def commutation():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        return render_template('commutation.html', connections=[])

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, label FROM connections')
            connections = cur.fetchall()
            connections = [{'id': row[0], 'label': row[1]} for row in connections]
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        connections = []
    finally:
        conn.close()

    return render_template('commutation.html', connections=connections)

# Заглушки для других страниц
@app.route('/reference')
def reference():
    return "Справочник"

@app.route('/report')
def report():
    return "Отчеты"

@app.route('/help')
def help():
    return "Справка"

@app.route('/add_dc')
def add_dc():
    return "Добавление ЦОД"

@app.route('/add_user')
def add_user():
    return "Добавление пользователя"

@app.route('/reference_switches')
def reference_switches():
    return "Коммутаторы"

@app.route('/reference_servers')
def reference_servers():
    return "Серверы"

@app.route('/reference_roles')
def reference_roles():
    return "Матрица ролей"

@app.route('/reference_users')
def reference_users():
    return "Пользователи"

@app.route('/upload_connection')
def upload_connection():
    return "Загрузка подключения"

@app.route('/add_switch')
def add_switch():
    return "Добавление коммутатора"

# Динамический маршрут для дашборда
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session['role'] == 'Администратор':
        return redirect(url_for('admin_dashboard'))
    elif session['role'] == 'Инженер ЛВС':
        return redirect(url_for('engineer_dashboard'))
    else:
        return redirect(url_for('observer_dashboard'))

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
