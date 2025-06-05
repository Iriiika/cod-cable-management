from flask import Flask, render_template, request, redirect, url_for, flash, session, g, send_file, jsonify
from flask_babel import Babel, _
import psycopg
import bcrypt
import math
import io
from openpyxl import Workbook

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
app.config['LANGUAGES'] = ['ru', 'en']
babel = Babel(app)
DB_CONFIG = {
    'dbname': 'cod_db',
    'user': 'postgres',
    'password': 'password123',
    'host': 'localhost',
    'port': '5432'
}

# Функция выбора локали (без устаревшего декоратора localeselector)
def get_locale():
    if 'lang' in session:
        return session['lang']
    return request.accept_languages.best_match(app.config['LANGUAGES'])

# Регистрируем функцию выбора локали
babel.init_app(app, locale_selector=get_locale)

def get_db_connection():
    try:
        conn = psycopg.connect(**DB_CONFIG)
        return conn
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        return None

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message=_("Страница не найдена")), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, error_message=_("Доступ запрещен")), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message=_("Внутренняя ошибка сервера")), 500

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['username']
        password = request.form['password'].encode('utf-8')
        conn = get_db_connection()
        if conn is None:
            return render_template('login.html', error=_('Ошибка сервера'))
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
                return render_template('login.html', error=_('Запросите доступ у <a href="mailto:SergeyAIvanov@dom.ru">SergeyAIvanov@dom.ru</a>'))
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
            flash(_('Ошибка базы данных'), 'error')
            return redirect(url_for('register'))
        try:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO users (full_name, role, login, password, email) VALUES (%s, %s, %s, %s, %s)', 
                            (full_name, 'Наблюдатель', login, hashed_password, email))
                conn.commit()
                cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                            (session.get('user_id', 0), 'Регистрация пользователя', login))
                conn.commit()
                flash(_('Регистрация успешна! Запросите доступ у администратора для повышения роли.'), 'success')
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
        return render_template('reference.html', data_centers=[], page=1, total_pages=1)
    per_page = 10
    page = int(request.args.get('page', 1))
    if page < 1:
        page = 1
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM data_centers')
            total_records = cur.fetchone()[0]
            total_pages = math.ceil(total_records / per_page)
            if page > total_pages and total_pages > 0:
                page = total_pages
            offset = (page - 1) * per_page
            cur.execute('SELECT id, name, short_name FROM data_centers LIMIT %s OFFSET %s', (per_page, offset))
            data_centers = cur.fetchall()
            data_centers = [{'id': row[0], 'name': row[1], 'short_name': row[2]} for row in data_centers]
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        data_centers = []
        total_pages = 1
        page = 1
    finally:
        conn.close()
    return render_template('reference.html', data_centers=data_centers, page=page, total_pages=total_pages)

@app.route('/update_data_center/<int:dc_id>', methods=['POST'])
def update_data_center(dc_id):
    if 'user_id' not in session or session['role'] != 'Администратор':
        return jsonify({'error': _('Доступ запрещен')}), 403
    data = request.get_json()
    name = data.get('name')
    short_name = data.get('short_name')
    if not name or not short_name:
        return jsonify({'error': _('Название и короткое имя обязательны')}), 400
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': _('Ошибка базы данных')}), 500
    try:
        with conn.cursor() as cur:
            cur.execute('UPDATE data_centers SET name = %s, short_name = %s WHERE id = %s', (name, short_name, dc_id))
            if cur.rowcount == 0:
                return jsonify({'error': _('ЦОД не найден')}), 404
            conn.commit()
            cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                        (session['user_id'], 'Редактирование ЦОД', name))
            conn.commit()
        return jsonify({'success': _('ЦОД успешно отредактирован')})
    except psycopg.Error as e:
        return jsonify({'error': f'Ошибка базы: {e}'}), 500
    finally:
        conn.close()

@app.route('/export_data_centers')
def export_data_centers():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn is None:
        flash(_('Ошибка базы данных'), 'error')
        return redirect(url_for('reference'))
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, name, short_name FROM data_centers')
            data_centers = cur.fetchall()
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        return redirect(url_for('reference'))
    finally:
        conn.close()
    
    # Создаем Excel-файл
    wb = Workbook()
    ws = wb.active
    ws.title = "Data Centers"
    ws.append([_("ID"), _("Название"), _("Короткое имя")])
    for dc in data_centers:
        ws.append([dc[0], dc[1], dc[2]])
    
    # Сохраняем файл в буфер
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name="data_centers.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

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

@app.route('/delete_switch/<int:switch_id>', methods=['POST'])
def delete_switch(switch_id):
    if 'user_id' not in session or session['role'] != 'Инженер ЛВС':
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn is None:
        flash(_('Ошибка базы данных'), 'error')
        return redirect(url_for('reference_switches'))
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT hostname FROM switches WHERE id = %s', (switch_id,))
            switch_hostname = cur.fetchone()
            if not switch_hostname:
                flash(_('Коммутатор не найден'), 'error')
                return redirect(url_for('reference_switches'))
            switch_hostname = switch_hostname[0]
            cur.execute('DELETE FROM switches WHERE id = %s', (switch_id,))
            conn.commit()
            cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                        (session['user_id'], 'Удаление коммутатора', switch_hostname))
            conn.commit()
            flash(_('Коммутатор успешно удален'), 'success')
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('reference_switches'))

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

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user_by_id(user_id):
    if 'user_id' not in session or session['role'] != 'Администратор':
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn is None:
        flash(_('Ошибка базы данных'), 'error')
        return redirect(url_for('reference_users'))
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT login FROM users WHERE id = %s', (user_id,))
            user_login = cur.fetchone()
            if not user_login:
                flash(_('Пользователь не найден'), 'error')
                return redirect(url_for('reference_users'))
            user_login = user_login[0]
            cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
            conn.commit()
            cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                        (session['user_id'], 'Удаление пользователя', user_login))
            conn.commit()
            flash(_('Пользователь успешно удален'), 'success')
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('reference_users'))

@app.route('/add_dc', methods=['GET', 'POST'])
def add_dc():
    if 'user_id' not in session or session['role'] != 'Администратор':
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        short_name = request.form['short_name']
        conn = get_db_connection()
        if conn is None:
            flash(_('Ошибка базы данных'), 'error')
            return redirect(url_for('add_dc'))
        try:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO data_centers (name, short_name) VALUES (%s, %s)', (name, short_name))
                conn.commit()
                cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                            (session['user_id'], 'Добавление ЦОД', name))
                conn.commit()
                flash(_('ЦОД успешно добавлен'), 'success')
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
            flash(_('Ошибка базы данных'), 'error')
            return redirect(url_for('add_user'))
        try:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO users (full_name, role, login, password, email) VALUES (%s, %s, %s, %s, %s)', 
                            (full_name, role, login, hashed_password, email))
                conn.commit()
                cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                            (session['user_id'], 'Добавление пользователя', login))
                conn.commit()
                flash(_('Пользователь успешно добавлен'), 'success')
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
            flash(_('Ошибка базы данных'), 'error')
            return redirect(url_for('add_switch'))
        try:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO switches (rack_id, type, hostname, unit, port_srvm, port_data) VALUES (%s, %s, %s, %s, %s, %s)', 
                            (rack_id, type, hostname, unit, port_srvm, port_data))
                conn.commit()
                cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                            (session['user_id'], 'Добавление коммутатора', hostname))
                conn.commit()
                flash(_('Коммутатор успешно добавлен'), 'success')
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
            flash(_('Ошибка базы данных'), 'error')
            return redirect(url_for('upload_connection'))
        try:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO connections (server_id, switch_id, port, label) VALUES (%s, %s, %s, %s)', 
                            (server_id, switch_id, port, label))
                conn.commit()
                cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                            (session['user_id'], 'Загрузка подключения', label))
                conn.commit()
                flash(_('Подключение успешно загружено'), 'success')
                return redirect(url_for('commutation'))
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()
    return render_template('upload_connection.html')

@app.route('/delete_connection/<int:conn_id>', methods=['POST'])
def delete_connection(conn_id):
    if 'user_id' not in session or session['role'] != 'Инженер ЛВС':
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn is None:
        flash(_('Ошибка базы данных'), 'error')
        return redirect(url_for('commutation'))
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT label FROM connections WHERE id = %s', (conn_id,))
            conn_label = cur.fetchone()
            if not conn_label:
                flash(_('Подключение не найдено'), 'error')
                return redirect(url_for('commutation'))
            conn_label = conn_label[0]
            cur.execute('DELETE FROM connections WHERE id = %s', (conn_id,))
            conn.commit()
            cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                        (session['user_id'], 'Удаление подключения', conn_label))
            conn.commit()
            flash(_('Подключение успешно удалено'), 'success')
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('commutation'))

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
        flash(_('Ошибка базы данных'), 'error')
        return redirect(url_for('settings'))
    if request.method == 'POST':
        label_format = request.form['label_format']
        export_limit = request.form['export_limit']
        try:
            with conn.cursor() as cur:
                cur.execute('UPDATE settings SET value = %s WHERE key = %s', (label_format, 'label_format'))
                cur.execute('UPDATE settings SET value = %s WHERE key = %s', (export_limit, 'export_limit'))
                conn.commit()
                cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                            (session['user_id'], 'Изменение настроек', 'label_format, export_limit'))
                conn.commit()
                flash(_('Настройки успешно обновлены'), 'success')
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('settings'))
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT key, value FROM settings')
            settings_data = cur.fetchall()
            settings = {row[0]: row[1] for row in settings_data}
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
        settings = {'label_format': '', 'export_limit': '1000'}
    finally:
        conn.close()
    return render_template('settings.html', settings=settings)

@app.route('/delete_dc', methods=['GET', 'POST'])
def delete_dc():
    if 'user_id' not in session or session['role'] != 'Администратор':
        return redirect(url_for('login'))
    if request.method == 'POST':
        dc_id = int(request.form['dc_id'])
        conn = get_db_connection()
        if conn is None:
            flash(_('Ошибка базы данных'), 'error')
            return redirect(url_for('delete_dc'))
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT name FROM data_centers WHERE id = %s', (dc_id,))
                dc_name = cur.fetchone()[0]
                cur.execute('DELETE FROM data_centers WHERE id = %s', (dc_id,))
                conn.commit()
                cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                            (session['user_id'], 'Удаление ЦОД', dc_name))
                conn.commit()
                flash(_('ЦОД успешно удален'), 'success')
                return redirect(url_for('reference'))
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()
    return render_template('delete_dc.html')

@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if 'user_id' not in session or session['role'] != 'Администратор':
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        conn = get_db_connection()
        if conn is None:
            flash(_('Ошибка базы данных'), 'error')
            return redirect(url_for('delete_user'))
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT login FROM users WHERE id = %s', (user_id,))
                user_login = cur.fetchone()[0]
                cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
                conn.commit()
                cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                            (session['user_id'], 'Удаление пользователя', user_login))
                conn.commit()
                flash(_('Пользователь успешно удален'), 'success')
                return redirect(url_for('reference_users'))
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()
    return render_template('delete_user.html')

@app.route('/edit_dc', methods=['GET', 'POST'])
def edit_dc():
    if 'user_id' not in session or session['role'] != 'Администратор':
        return redirect(url_for('login'))
    if request.method == 'POST':
        dc_id = int(request.form['dc_id'])
        name = request.form['name']
        short_name = request.form['short_name']
        conn = get_db_connection()
        if conn is None:
            flash(_('Ошибка базы данных'), 'error')
            return redirect(url_for('edit_dc'))
        try:
            with conn.cursor() as cur:
                cur.execute('UPDATE data_centers SET name = %s, short_name = %s WHERE id = %s', (name, short_name, dc_id))
                conn.commit()
                cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                            (session['user_id'], 'Редактирование ЦОД', name))
                conn.commit()
                flash(_('ЦОД успешно отредактирован'), 'success')
                return redirect(url_for('reference'))
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()
    return render_template('edit_dc.html')

@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    if 'user_id' not in session or session['role'] != 'Администратор':
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        full_name = request.form['full_name']
        role = request.form['role']
        login = request.form['login']
        password = request.form['password']
        email = request.form['email']
        conn = get_db_connection()
        if conn is None:
            flash(_('Ошибка базы данных'), 'error')
            return redirect(url_for('edit_user'))
        try:
            with conn.cursor() as cur:
                if password:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cur.execute('UPDATE users SET full_name = %s, role = %s, login = %s, password = %s, email = %s WHERE id = %s',
                                (full_name, role, login, hashed_password, email, user_id))
                else:
                    cur.execute('UPDATE users SET full_name = %s, role = %s, login = %s, email = %s WHERE id = %s',
                                (full_name, role, login, email, user_id))
                conn.commit()
                cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                            (session['user_id'], 'Редактирование пользователя', login))
                conn.commit()
                flash(_('Пользователь успешно отредактирован'), 'success')
                return redirect(url_for('reference_users'))
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()
    return render_template('edit_user.html')

@app.route('/edit_switch', methods=['GET', 'POST'])
def edit_switch():
    if 'user_id' not in session or session['role'] != 'Инженер ЛВС':
        return redirect(url_for('login'))
    if request.method == 'POST':
        switch_id = int(request.form['switch_id'])
        rack_id = int(request.form['rack_id'])
        type = request.form['type']
        hostname = request.form['hostname']
        unit = int(request.form['unit'])
        port_srvm = request.form['port_srvm'] or None
        port_data = request.form['port_data'] or None
        conn = get_db_connection()
        if conn is None:
            flash(_('Ошибка базы данных'), 'error')
            return redirect(url_for('edit_switch'))
        try:
            with conn.cursor() as cur:
                cur.execute('UPDATE switches SET rack_id = %s, type = %s, hostname = %s, unit = %s, port_srvm = %s, port_data = %s WHERE id = %s',
                            (rack_id, type, hostname, unit, port_srvm, port_data, switch_id))
                conn.commit()
                cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                            (session['user_id'], 'Редактирование коммутатора', hostname))
                conn.commit()
                flash(_('Коммутатор успешно отредактирован'), 'success')
                return redirect(url_for('reference_switches'))
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()
    return render_template('edit_switch.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn is None:
        flash(_('Ошибка базы данных'), 'error')
        return redirect(url_for('dashboard'))
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT full_name, email FROM users WHERE id = %s', (session['user_id'],))
            user = cur.fetchone()
            if not user:
                flash(_('Пользователь не найден'), 'error')
                return redirect(url_for('dashboard'))
            user_data = {'full_name': user[0], 'email': user[1]}
        if request.method == 'POST':
            full_name = request.form['full_name']
            email = request.form['email']
            password = request.form['password']
            with conn.cursor() as cur:
                if password:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cur.execute('UPDATE users SET full_name = %s, email = %s, password = %s WHERE id = %s',
                                (full_name, email, hashed_password, session['user_id']))
                else:
                    cur.execute('UPDATE users SET full_name = %s, email = %s WHERE id = %s',
                                (full_name, email, session['user_id']))
                conn.commit()
                cur.execute('INSERT INTO logs (user_id, action, object) VALUES (%s, %s, %s)', 
                            (session['user_id'], 'Редактирование профиля', session['full_name']))
                conn.commit()
                session['full_name'] = full_name
                flash(_('Профиль успешно обновлен'), 'success')
                return redirect(url_for('profile'))
    except psycopg.Error as e:
        flash(f'Ошибка базы: {e}', 'error')
    finally:
        conn.close()
    return render_template('profile.html', user=user_data)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        if conn is None:
            flash(_('Ошибка базы данных'), 'error')
            return redirect(url_for('reset_password'))
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT id FROM users WHERE email = %s', (email,))
                user = cur.fetchone()
            if user:
                flash(_('Инструкции по сбросу пароля отправлены на ваш email.'), 'success')
            else:
                flash(_('Пользователь с таким email не найден.'), 'error')
        except psycopg.Error as e:
            flash(f'Ошибка базы: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    session.clear()
    flash(_('Вы успешно вышли из системы.'), 'success')
    return redirect(url_for('login'))

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
    
@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in app.config['LANGUAGES']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)