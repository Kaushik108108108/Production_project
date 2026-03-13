from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth_bp = Blueprint('auth', __name__)

# ── Dummy credentials (replace with Oracle DB lookup later) ──
ADMIN_USERS   = {'admin': 'admin123', 'principal': 'pass123'}
STUDENT_USERS = {'STU-001': {'email': 'john@school.edu', 'password': 'pass123', 'name': 'John Doe'},
                 'STU-002': {'email': 'jane@school.edu', 'password': 'pass123', 'name': 'Jane Smith'}}

# ────────────────────────────────────────────
#  LANDING
# ────────────────────────────────────────────
@auth_bp.route('/')
def index():
    return render_template('shared/index.html')

# ────────────────────────────────────────────
#  ADMIN AUTH
# ────────────────────────────────────────────
@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if ADMIN_USERS.get(username) == password:
            session['admin_logged_in'] = True
            session['admin_user']      = username
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('admin/login.html')

@auth_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    return redirect(url_for('auth.admin_login'))

# ────────────────────────────────────────────
#  STUDENT AUTH
# ────────────────────────────────────────────
@auth_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        email      = request.form.get('email', '').strip()
        password   = request.form.get('password', '').strip()
        user = STUDENT_USERS.get(student_id)
        if user and user['email'] == email and user['password'] == password:
            session['student_logged_in'] = True
            session['student_id']        = student_id
            session['student_name']      = user['name']
            return redirect(url_for('student.dashboard'))
        flash('Invalid credentials. Check your Student ID, email and password.', 'error')
    return render_template('student/login.html')

@auth_bp.route('/student/logout')
def student_logout():
    session.pop('student_logged_in', None)
    session.pop('student_id', None)
    session.pop('student_name', None)
    return redirect(url_for('auth.student_login'))
