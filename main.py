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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name = request.form['full_name']
        login = request.form['login']
        password = request.form['password'].encode('utf-8')
        email = request.form['email']

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        conn = get_db_connection()
        if conn is None:
            flash('Ошибка базы данных', 'error')
            return redirect(url_for('register'))

        try:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO users (full_name, role, login, password, email) VALUES (%s, %s, %s, %s, %s)', 
                            (full_name, 'Наблюдатель', login, hashed_password, email))
                conn.commit()
                flash('Регистрация успешна! Запросите доступ у администратора для повышения роли.', 'success')
                return redirect(url_for('login'))
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()

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

@app.route('/reference_servers')
def reference_servers():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        return render_template('reference_servers.html', servers=[])

    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT s.id, s.serial_number, dc.name AS dc_name, h.name AS hall_name, r.name AS rack_name, s.unit
                FROM servers s
                JOIN racks r ON s.rack_id = r.id
                JOIN halls h ON r.hall_id = h.id
                JOIN data_centers dc ON h.data_center_id = dc.id
            ''')
            servers = cur.fetchall()
            servers = [{
                'id': row[0],
                'serial_number': row[1],
                'dc_name': row[2],
                'hall_name': row[3],
                'rack_name': row[4],
                'unit': row[5]
            } for row in servers]
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        servers = []
    finally:
        conn.close()

    return render_template('reference_servers.html', servers=servers)

@app.route('/reference_roles')
def reference_roles():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        return render_template('reference_roles.html', roles=[])

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT name, permissions FROM roles')
            roles = cur.fetchall()
            roles = [{'name': row[0], 'permissions': row[1]} for row in roles]
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        roles = []
    finally:
        conn.close()

    return render_template('reference_roles.html', roles=roles)

@app.route('/reference_users')
def reference_users():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        return render_template('reference_users.html', users=[])

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, full_name, role, login, email FROM users')
            users = cur.fetchall()
            users = [{
                'id': row[0],
                'full_name': row[1],
                'role': row[2],
                'login': row[3],
                'email': row[4]
            } for row in users]
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        users = []
    finally:
        conn.close()

    return render_template('reference_users.html', users=users)

@app.route('/add_dc', methods=['GET', 'POST'])
def add_dc():
    if 'user_id' not in session or session['role'] != 'Администратор':
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        short_name = request.form['short_name']

        conn = get_db_connection()
        if conn is None:
            flash('Ошибка базы данных', 'error')
            return redirect(url_for('add_dc'))

        try:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO data_centers (name, short_name) VALUES (%s, %s)', (name, short_name))
                conn.commit()
                flash('ЦОД успешно добавлен', 'success')
                return redirect(url_for('reference'))
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()

    return render_template('add_dc.html')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session or session['role'] != 'Администратор':
        return redirect(url_for('login'))

    if request.method == 'POST':
        full_name = request.form['full_name']
        role = request.form['role']
        login = request.form['login']
        password = request.form['password'].encode('utf-8')
        email = request.form['email']

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        conn = get_db_connection()
        if conn is None:
            flash('Ошибка базы данных', 'error')
            return redirect(url_for('add_user'))

        try:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO users (full_name, role, login, password, email) VALUES (%s, %s, %s, %s, %s)', 
                            (full_name, role, login, hashed_password, email))
                conn.commit()
                flash('Пользователь успешно добавлен', 'success')
                return redirect(url_for('reference_users'))
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()

    return render_template('add_user.html')

@app.route('/add_switch', methods=['GET', 'POST'])
def add_switch():
    if 'user_id' not in session or session['role'] != 'Инженер ЛВС':
        return redirect(url_for('login'))

    if request.method == 'POST':
        rack_id = int(request.form['rack_id'])
        type = request.form['type']
        hostname = request.form['hostname']
        unit = int(request.form['unit'])
        port_srvm = request.form['port_srvm'] or None
        port_data = request.form['port_data'] or None

        conn = get_db_connection()
        if conn is None:
            flash('Ошибка базы данных', 'error')
            return redirect(url_for('add_switch'))

        try:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO switches (rack_id, type, hostname, unit, port_srvm, port_data) VALUES (%s, %s, %s, %s, %s, %s)', 
                            (rack_id, type, hostname, unit, port_srvm, port_data))
                conn.commit()
                flash('Коммутатор успешно добавлен', 'success')
                return redirect(url_for('reference_switches'))
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()

    return render_template('add_switch.html')

@app.route('/upload_connection', methods=['GET', 'POST'])
def upload_connection():
    if 'user_id' not in session or session['role'] != 'Инженер ЛВС':
        return redirect(url_for('login'))

    if request.method == 'POST':
        server_id = int(request.form['server_id'])
        switch_id = int(request.form['switch_id'])
        port = request.form['port']
        label = request.form['label']

        conn = get_db_connection()
        if conn is None:
            flash('Ошибка базы данных', 'error')
            return redirect(url_for('upload_connection'))

        try:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO connections (server_id, switch_id, port, label) VALUES (%s, %s, %s, %s)', 
                            (server_id, switch_id, port, label))
                conn.commit()
                flash('Подключение успешно загружено', 'success')
                return redirect(url_for('commutation'))
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()

    return render_template('upload_connection.html')

@app.route('/report')
def report():
    if 'user_id' not in session or session['role'] not in ['Администратор', 'Наблюдатель']:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        return render_template('report.html', reports=[])

    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT dc.name AS dc_name, h.name AS hall_name, r.name AS rack_name, COUNT(c.id) AS connection_count
                FROM connections c
                JOIN servers s ON c.server_id = s.id
                JOIN switches sw ON c.switch_id = sw.id
                JOIN racks r ON s.rack_id = r.id
                JOIN halls h ON r.hall_id = h.id
                JOIN data_centers dc ON h.data_center_id = dc.id
                GROUP BY dc.name, h.name, r.name
            ''')
            reports = cur.fetchall()
            reports = [{
                'dc_name': row[0],
                'hall_name': row[1],
                'rack_name': row[2],
                'connection_count': row[3]
            } for row in reports]
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        reports = []
    finally:
        conn.close()

    return render_template('report.html', reports=reports)

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/logs')
def logs():
    if 'user_id' not in session or session['role'] != 'Администратор':
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        return render_template('logs.html', logs=[])

    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT u.full_name AS user_name, l.action, l.object, l.created_at
                FROM logs l
                JOIN users u ON l.user_id = u.id
                ORDER BY l.created_at DESC
            ''')
            logs = cur.fetchall()
            logs = [{
                'user_name': row[0],
                'action': row[1],
                'object': row[2],
                'created_at': row[3]
            } for row in logs]
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        logs = []
    finally:
        conn.close()

    return render_template('logs.html', logs=logs)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session or session['role'] != 'Администратор':
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        flash('Ошибка базы данных', 'error')
        return redirect(url_for('settings'))

    try:
        with conn.cursor() as cur:
            if request.method == 'POST':
                label_format = request.form['label_format']
                export_limit = request.form['export_limit']

                cur.execute('INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value', 
                            ('label_format', label_format))
                cur.execute('INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value', 
                            ('export_limit', export_limit))
                conn.commit()
                flash('Настройки успешно сохранены', 'success')
                return redirect(url_for('settings'))

            cur.execute('SELECT key, value FROM settings')
            settings_data = cur.fetchall()
            settings = {row[0]: row[1] for row in settings_data}
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
    finally:
        conn.close()

    return render_template('settings.html', settings=settings)

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