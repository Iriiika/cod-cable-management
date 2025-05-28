from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DB_CONFIG = {
    'dbname': 'cod_db',
    'user': 'postgres',
    'password': 'password123',
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    try:
        conn = psycopg.connect(**DB_CONFIG)
        return conn
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        return None

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
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Запросите доступ у <a href="mailto:SergeyAIvanov@dom.ru">SergeyAIvanov@dom.ru</a>')
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()

    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

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

@app.route('/reference')
def reference():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        return render_template('reference.html', data_centers=[])

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT name, short_name FROM data_centers')
            data_centers = cur.fetchall()
            data_centers = [{'name': row[0], 'short_name': row[1]} for row in data_centers]
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        data_centers = []
    finally:
        conn.close()

    return render_template('reference.html', data_centers=data_centers)

@app.route('/reference_switches')
def reference_switches():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        return render_template('reference_switches.html', switches=[])

    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT s.id, s.hostname, dc.name AS dc_name, h.name AS hall_name, r.name AS rack_name
                FROM switches s
                JOIN racks r ON s.rack_id = r.id
                JOIN halls h ON r.hall_id = h.id
                JOIN data_centers dc ON h.data_center_id = dc.id
            ''')
            switches = cur.fetchall()
            switches = [{
                'id': row[0],
                'hostname': row[1],
                'dc_name': row[2],
                'hall_name': row[3],
                'rack_name': row[4]
            } for row in switches]
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        switches = []
    finally:
        conn.close()

    return render_template('reference_switches.html', switches=switches)

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/add_dc')
def add_dc():
    return render_template('add_dc.html')

@app.route('/add_user')
def add_user():
    return render_template('add_user.html')

@app.route('/reference_servers')
def reference_servers():
    return render_template('reference_servers.html')

@app.route('/reference_roles')
def reference_roles():
    return render_template('reference_roles.html')

@app.route('/reference_users')
def reference_users():
    return render_template('reference_users.html')

@app.route('/upload_connection')
def upload_connection():
    return render_template('upload_connection.html')

@app.route('/add_switch')
def add_switch():
    return render_template('add_switch.html')

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

if __name__ == '__main__':
    app.run(debug=True)