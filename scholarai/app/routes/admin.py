from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated

# ── Mock data (replace with Oracle DB queries later) ──
STUDENTS = [
    {'id':'STU-001','name':'John Doe',     'cls':'10A','sec':'A','pi':72,'risk':'high',  'att':68,'dues':4500,'complaints':2},
    {'id':'STU-002','name':'Jane Smith',   'cls':'10B','sec':'B','pi':91,'risk':'low',   'att':95,'dues':0,   'complaints':0},
    {'id':'STU-003','name':'Peter Jones',  'cls':'10A','sec':'A','pi':58,'risk':'high',  'att':55,'dues':8200,'complaints':3},
    {'id':'STU-004','name':'Maria Garcia', 'cls':'11A','sec':'A','pi':78,'risk':'medium','att':80,'dues':1200,'complaints':1},
    {'id':'STU-005','name':'James Wilson', 'cls':'11B','sec':'B','pi':85,'risk':'low',   'att':92,'dues':0,   'complaints':0},
    {'id':'STU-006','name':'Aisha Malik',  'cls':'10A','sec':'C','pi':61,'risk':'high',  'att':60,'dues':6000,'complaints':1},
]

STUDENT_DETAIL = {
    'id':'STU-001','name':'John Doe','cls':'10A','sec':'A',
    'email':'john.doe@school.edu','guardian':'Mark Doe','phone':'+91-9876543210',
    'pi':72,'risk':'high','confidence':87,'dues':4500,
    'complaints':[
        {'type':'DISCIPLINARY','date':'Feb 12, 2026','note':'Disruptive behavior in classroom during exam period.','severity':'HIGH'},
        {'type':'ATTENDANCE',  'date':'Jan 08, 2026','note':'3 consecutive unexplained absences.','severity':'MEDIUM'},
    ],
    'subjects':[
        {'name':'Mathematics',       'att':68,'t1':72,'t2':68,'t3':65,'pred':62,'rec':'Enroll in extra tutoring. Focus on algebra & calculus.'},
        {'name':'Science',           'att':80,'t1':78,'t2':82,'t3':79,'pred':81,'rec':'Good trajectory. Review practical experiment reports.'},
        {'name':'English',           'att':90,'t1':88,'t2':85,'t3':90,'pred':91,'rec':'Excellent. Continue wide reading and essay practice.'},
        {'name':'History',           'att':70,'t1':60,'t2':58,'t3':55,'pred':50,'rec':'Critical: Attendance low. Focus on key historical events.'},
        {'name':'Geography',         'att':75,'t1':70,'t2':72,'t3':74,'pred':76,'rec':'Steady improvement. Review map work and case studies.'},
        {'name':'Computer Science',  'att':88,'t1':82,'t2':88,'t3':90,'pred':93,'rec':'Excellent. Explore advanced programming competitions.'},
        {'name':'Physical Education','att':95,'t1':90,'t2':92,'t3':93,'pred':94,'rec':'Outstanding. Maintain current habits and fitness routine.'},
    ]
}

PREDICTIONS = [
    {'id':'PRD-047','student':'John Doe', 'cls':'10A','subject':'Mathematics',    'score':62,'risk':'high',  'confidence':87,'by':'Admin',   'date':'Mar 01, 2026'},
    {'id':'PRD-046','student':'Jane Smith','cls':'10B','subject':'Science',       'score':91,'risk':'low',   'confidence':94,'by':'Student', 'date':'Feb 28, 2026'},
    {'id':'PRD-045','student':'Peter Jones','cls':'10A','subject':'History',      'score':50,'risk':'high',  'confidence':91,'by':'Admin',   'date':'Feb 25, 2026'},
    {'id':'PRD-044','student':'Maria Garcia','cls':'11A','subject':'English',     'score':76,'risk':'medium','confidence':79,'by':'Admin',   'date':'Feb 22, 2026'},
    {'id':'PRD-043','student':'James Wilson','cls':'11B','subject':'Comp. Science','score':93,'risk':'low', 'confidence':96,'by':'Student', 'date':'Feb 18, 2026'},
]

CHAT_HISTORY = [
    {'id':1,'label':'Today — Risk Analysis Session'},
    {'id':2,'label':'Mar 08 — Bulk Email Draft'},
    {'id':3,'label':'Mar 05 — Prediction Report'},
    {'id':4,'label':'Feb 28 — Attendance Review'},
]

# ────────────────────────────────────────────────────────────
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = {
        'total': len(STUDENTS),
        'high':  sum(1 for s in STUDENTS if s['risk']=='high'),
        'medium':sum(1 for s in STUDENTS if s['risk']=='medium'),
        'avg_pi':round(sum(s['pi'] for s in STUDENTS)/len(STUDENTS)),
    }
    cls_filter  = request.args.get('cls', '')
    sec_filter  = request.args.get('sec', '')
    risk_filter = request.args.get('risk', '')
    students = STUDENTS
    if cls_filter:  students = [s for s in students if cls_filter in s['cls']]
    if sec_filter:  students = [s for s in students if s['sec'] == sec_filter]
    if risk_filter: students = [s for s in students if s['risk'] == risk_filter]
    return render_template('admin/dashboard.html', stats=stats, students=students,
                           cls_filter=cls_filter, sec_filter=sec_filter, risk_filter=risk_filter)

@admin_bp.route('/student/<student_id>')
@admin_required
def student_details(student_id):
    # In real app: query Oracle DB by student_id
    return render_template('admin/student_details.html', student=STUDENT_DETAIL)

@admin_bp.route('/send-email', methods=['GET', 'POST'])
@admin_bp.route('/send-email/<student_id>', methods=['GET', 'POST'])
@admin_required
def send_email(student_id='STU-001'):
    student = next((s for s in STUDENTS if s['id']==student_id), STUDENTS[0])
    if request.method == 'POST':
        flash('Email sent successfully!', 'success')
        return redirect(url_for('admin.student_details', student_id=student_id))
    return render_template('admin/send_email.html', student=student)

@admin_bp.route('/predictions')
@admin_required
def predictions():
    return render_template('admin/predictions.html', predictions=PREDICTIONS)

@admin_bp.route('/reports')
@admin_required
def reports():
    return render_template('admin/reports.html')

@admin_bp.route('/chatbot')
@admin_required
def chatbot():
    return render_template('admin/chatbot.html', chat_history=CHAT_HISTORY)

@admin_bp.route('/chatbot/send', methods=['POST'])
@admin_required
def chatbot_send():
    """API endpoint for chatbot messages — wire to LLM later"""
    msg = request.json.get('message', '')
    # Placeholder response — replace with actual AI call
    responses = {
        'high risk': '12 students are currently HIGH RISK. Top 3: John Doe (PI:72%), Peter Jones (PI:58%), Aisha Malik (PI:61%). Shall I draft emails?',
        'attendance': 'Class 10A has the lowest average attendance at 64%. 3 students are below the 75% threshold.',
        'default': f'I received your query: "{msg}". Analyzing the student database and prediction models to provide a detailed answer...'
    }
    msg_lower = msg.lower()
    if 'high risk' in msg_lower:     reply = responses['high risk']
    elif 'attendance' in msg_lower:  reply = responses['attendance']
    else:                            reply = responses['default']
    return jsonify({'reply': reply})
