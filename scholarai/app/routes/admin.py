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

# ── Mock data — keys match Oracle DB column names ──
STUDENTS = [
    {'student_id':'STU-001','full_name':'John Doe',     'class_level':'10A','section':'A','performance_index':72,'risk_level':'high',  'attendance_rate':68,'due_amount':4500,'complaint_count':2},
    {'student_id':'STU-002','full_name':'Jane Smith',   'class_level':'10B','section':'B','performance_index':91,'risk_level':'low',   'attendance_rate':95,'due_amount':0,   'complaint_count':0},
    {'student_id':'STU-003','full_name':'Peter Jones',  'class_level':'10A','section':'A','performance_index':58,'risk_level':'high',  'attendance_rate':55,'due_amount':8200,'complaint_count':3},
    {'student_id':'STU-004','full_name':'Maria Garcia', 'class_level':'11A','section':'A','performance_index':78,'risk_level':'medium','attendance_rate':80,'due_amount':1200,'complaint_count':1},
    {'student_id':'STU-005','full_name':'James Wilson', 'class_level':'11B','section':'B','performance_index':85,'risk_level':'low',   'attendance_rate':92,'due_amount':0,   'complaint_count':0},
    {'student_id':'STU-006','full_name':'Aisha Malik',  'class_level':'10A','section':'C','performance_index':61,'risk_level':'high',  'attendance_rate':60,'due_amount':6000,'complaint_count':1},
]

STUDENT_DETAIL = {
    'student_id':'STU-001','full_name':'John Doe','class_level':'10A','section':'A',
    'email':'john.doe@school.edu','guardian_name':'Mark Doe','phone_number':'+91-9876543210',
    'performance_index':72,'risk_level':'high','confidence_score':87,'due_amount':4500,
    'complaint':[
        {'complaint_type':'DISCIPLINARY','recorded_at':'Feb 12, 2026','description':'Disruptive behavior in classroom during exam period.','severity':'HIGH'},
        {'complaint_type':'ATTENDANCE',  'recorded_at':'Jan 08, 2026','description':'3 consecutive unexplained absences.','severity':'MEDIUM'},
    ],
    'academic_record':[
        {'subject_name':'Mathematics',       'attendance_rate':68,'term1_score':72,'term2_score':68,'term3_score':65,'predicted_score':62,'ai_recommendation':'Enroll in extra tutoring. Focus on algebra & calculus.'},
        {'subject_name':'Science',           'attendance_rate':80,'term1_score':78,'term2_score':82,'term3_score':79,'predicted_score':81,'ai_recommendation':'Good trajectory. Review practical experiment reports.'},
        {'subject_name':'English',           'attendance_rate':90,'term1_score':88,'term2_score':85,'term3_score':90,'predicted_score':91,'ai_recommendation':'Excellent. Continue wide reading and essay practice.'},
        {'subject_name':'History',           'attendance_rate':70,'term1_score':60,'term2_score':58,'term3_score':55,'predicted_score':50,'ai_recommendation':'Critical: Attendance low. Focus on key historical events.'},
        {'subject_name':'Geography',         'attendance_rate':75,'term1_score':70,'term2_score':72,'term3_score':74,'predicted_score':76,'ai_recommendation':'Steady improvement. Review map work and case studies.'},
        {'subject_name':'Computer Science',  'attendance_rate':88,'term1_score':82,'term2_score':88,'term3_score':90,'predicted_score':93,'ai_recommendation':'Excellent. Explore advanced programming competitions.'},
        {'subject_name':'Physical Education','attendance_rate':95,'term1_score':90,'term2_score':92,'term3_score':93,'predicted_score':94,'ai_recommendation':'Outstanding. Maintain current habits and fitness routine.'},
    ]
}

PREDICTIONS = [
    {'prediction_id':'PRD-047','full_name':'John Doe',    'class_level':'10A','subject_name':'Mathematics',    'predicted_score':62,'risk_level':'high',  'confidence_score':87,'predicted_by':'Admin',   'created_at':'Mar 01, 2026'},
    {'prediction_id':'PRD-046','full_name':'Jane Smith',  'class_level':'10B','subject_name':'Science',        'predicted_score':91,'risk_level':'low',   'confidence_score':94,'predicted_by':'Student', 'created_at':'Feb 28, 2026'},
    {'prediction_id':'PRD-045','full_name':'Peter Jones', 'class_level':'10A','subject_name':'History',        'predicted_score':50,'risk_level':'high',  'confidence_score':91,'predicted_by':'Admin',   'created_at':'Feb 25, 2026'},
    {'prediction_id':'PRD-044','full_name':'Maria Garcia','class_level':'11A','subject_name':'English',        'predicted_score':76,'risk_level':'medium','confidence_score':79,'predicted_by':'Admin',   'created_at':'Feb 22, 2026'},
    {'prediction_id':'PRD-043','full_name':'James Wilson','class_level':'11B','subject_name':'Comp. Science',  'predicted_score':93,'risk_level':'low',   'confidence_score':96,'predicted_by':'Student', 'created_at':'Feb 18, 2026'},
]

CHAT_SESSION = [
    {'session_id':1,'session_label':'Today — Risk Analysis Session'},
    {'session_id':2,'session_label':'Mar 08 — Bulk Email Draft'},
    {'session_id':3,'session_label':'Mar 05 — Prediction Report'},
    {'session_id':4,'session_label':'Feb 28 — Attendance Review'},
]

# ────────────────────────────────────────────────────────────
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = {
        'total':  len(STUDENTS),
        'high':   sum(1 for s in STUDENTS if s['risk_level']=='high'),
        'medium': sum(1 for s in STUDENTS if s['risk_level']=='medium'),
        'avg_pi': round(sum(s['performance_index'] for s in STUDENTS)/len(STUDENTS)),
    }
    cls_filter   = request.args.get('cls', '')
    sec_filter   = request.args.get('sec', '')
    risk_filter  = request.args.get('risk', '')
    search_query = request.args.get('q', '').strip().lower()

    students = STUDENTS
    if cls_filter:   students = [s for s in students if cls_filter in s['class_level']]
    if sec_filter:   students = [s for s in students if s['section'] == sec_filter]
    if risk_filter:  students = [s for s in students if s['risk_level'] == risk_filter]
    if search_query: students = [s for s in students if
                                 search_query in s['full_name'].lower() or
                                 search_query in s['student_id'].lower()]

    return render_template('admin/dashboard.html', stats=stats, students=students,
                           cls_filter=cls_filter, sec_filter=sec_filter,
                           risk_filter=risk_filter, search_query=request.args.get('q',''))

@admin_bp.route('/student/<student_id>')
@admin_required
def student_details(student_id):
    # Handle search from the search bar on this page
    q = request.args.get('q', '').strip().lower()
    if q:
        match = next((s for s in STUDENTS if
                      q in s['student_id'].lower() or
                      q in s['full_name'].lower()), None)
        if match:
            return redirect(url_for('admin.student_details', student_id=match['student_id']))
        flash(f'No student found matching "{request.args.get("q")}"', 'error')

    student = next((s for s in STUDENTS if s['student_id'] == student_id), None)
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('admin.dashboard'))

    detail = {
        'student_id':        student['student_id'],
        'full_name':         student['full_name'],
        'class_level':       student['class_level'],
        'section':           student['section'],
        'email':             student['full_name'].lower().replace(' ', '.') + '@school.edu',
        'guardian_name':     'Guardian of ' + student['full_name'],
        'phone_number':      '+91-9876543210',
        'performance_index': student['performance_index'],
        'risk_level':        student['risk_level'],
        'confidence_score':  87,
        'due_amount':        student['due_amount'],
        'complaint':         STUDENT_DETAIL['complaint'] if student['student_id'] == 'STU-001' else [],
        'academic_record':   STUDENT_DETAIL['academic_record'],
    }
    return render_template('admin/student_details.html', student=detail,
                           search_query=request.args.get('q', ''))

@admin_bp.route('/send-email', methods=['GET', 'POST'])
@admin_bp.route('/send-email/<student_id>', methods=['GET', 'POST'])
@admin_required
def send_email(student_id='STU-001'):
    student = next((s for s in STUDENTS if s['student_id']==student_id), STUDENTS[0])
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
    return render_template('admin/chatbot.html', chat_session=CHAT_SESSION)

@admin_bp.route('/chatbot/send', methods=['POST'])
@admin_required
def chatbot_send():
    msg = request.json.get('message', '')
    msg_lower = msg.lower()
    if 'high risk'    in msg_lower: reply = '12 students are currently HIGH RISK. Top 3: John Doe (PI:72%), Peter Jones (PI:58%), Aisha Malik (PI:61%). Shall I draft emails?'
    elif 'attendance' in msg_lower: reply = 'Class 10A has the lowest average attendance_rate at 64%. 3 students are below the 75% threshold.'
    else:                           reply = f'I received: "{msg}". Analyzing student database and prediction models...'
    return jsonify({'reply': reply})
