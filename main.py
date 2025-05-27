# Импорт необходимых библиотек
from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg
import bcrypt

# Инициализация Flask-приложения
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Замените на безопасный ключ в продакшене

# Настройки подключения к базе данных PostgreSQL
DB_CONFIG = {
    'dbname': 'cod_db',
    'user': 'postgres',
    'password': 'your_password_here',  # Замените на ваш пароль
    'host': 'localhost',
    'port': '5432'
}

# Функция для подключения к базе данных
def get_db_connection():
    try:
        conn = psycopg.connect(**DB_CONFIG)
        return conn
    except psycopg.Error as e:
        flash(f'Ошибка подключения к базе данных: {e}', 'error')
        return None

# Маршрут для страницы авторизации
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['username']
        password = request.form['password'].encode('utf-8')
        
        # Подключение к базе данных
        conn = get_db_connection()
        if conn is None:
            return render_template('login.html', error='Ошибка сервера')
        
        try:
            with conn.cursor() as cur:
                # Поиск пользователя по логину
                cur.execute('SELECT id, full_name, role, password FROM users WHERE login = %s', (login,))
                user = cur.fetchone()
                
                if user and bcrypt.checkpw(password, user[3].encode('utf-8')):
                    # Успешная авторизация
                    session['user_id'] = user[0]
                    session['full_name'] = user[1]
                    session['role'] = user[2]
                    
                    # Перенаправление в зависимости от роли
                    if user[2] == 'Администратор':
                        return redirect(url_for('admin_dashboard'))
                    elif user[2] == 'Инженер ЛВС':
                        return redirect(url_for('engineer_dashboard'))
                    else:
                        return redirect(url_for('observer_dashboard'))
                else:
                    # Неверный логин или пароль
                    return render_template('login.html', error='Запросите доступ у SergeyAIvanov@dom.ru')
        except psycopg.Error as e:
            flash(f'Ошибка базы данных: {e}', 'error')
        finally:
            conn.close()
    
    return render_template('login.html')

# Заглушки для дашбордов ролей
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'Администратор':
        return redirect(url_for('login'))
    return render_template('main_admin.html', full_name=session['full_name'])

@app.route('/engineer')
def engineer_dashboard():
    if 'user_id' not in session or session['role'] != 'Инженер ЛВС':
        return redirect(url_for('login'))
    return render_template('main_engineer.html', full_name=session['full_name'])

@app.route('/observer')
def observer_dashboard():
    if 'user_id' not in session or session['role'] != 'Наблюдатель':
        return redirect(url_for('login'))
    return render_template('main_observer.html', full_name=session['full_name'])

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)