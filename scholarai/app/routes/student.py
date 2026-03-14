from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify

student_bp = Blueprint('student', __name__)

def student_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('student_logged_in'):
            return redirect(url_for('auth.student_login'))
        return f(*args, **kwargs)
    return decorated

# ── Mock data — keys match Oracle DB column names ──
PREDICTION_HISTORY = [
    {'prediction_id':'PRD-001','created_at':'Mar 01, 2026','subject_name':'Mathematics',    'predicted_score':75,'performance_index':'Good',        'risk_level':'low',   'ai_recommendation':'Maintain current study habits and review weekly.'},
    {'prediction_id':'PRD-002','created_at':'Feb 18, 2026','subject_name':'Science',        'predicted_score':52,'performance_index':'Below Average','risk_level':'high',  'ai_recommendation':'Focus on practical experiments, attend extra sessions.'},
    {'prediction_id':'PRD-003','created_at':'Jan 30, 2026','subject_name':'English',        'predicted_score':88,'performance_index':'Excellent',    'risk_level':'low',   'ai_recommendation':'Continue reading widely. Explore creative writing.'},
    {'prediction_id':'PRD-004','created_at':'Jan 15, 2026','subject_name':'History',        'predicted_score':61,'performance_index':'Average',      'risk_level':'medium','ai_recommendation':'Review key events. Improve attendance urgently.'},
    {'prediction_id':'PRD-005','created_at':'Dec 20, 2025','subject_name':'Computer Science','predicted_score':92,'performance_index':'Excellent',   'risk_level':'low',   'ai_recommendation':'Outstanding. Consider competitions.'},
]

AI_RECS = [
    {'subject_name':'Mathematics',  'recommendation_text':'Focus on algebra. Chapters 3–4 need review. Attendance below threshold.',      'rec_type':'warning'},
    {'subject_name':'Science',      'recommendation_text':'Strong performance. Consider advanced practical experiments to boost further.', 'rec_type':'success'},
    {'subject_name':'History',      'recommendation_text':'URGENT: Attendance at 70%. Risk of exam disqualification if not improved.',    'rec_type':'danger'},
    {'subject_name':'English',      'recommendation_text':'Excellent. Continue reading widely and expand essay writing practice.',         'rec_type':'success'},
]

CHAT_SESSION = [
    {'session_id':1,'session_label':'Today — Study Advice'},
    {'session_id':2,'session_label':'Mar 05 — Science Review'},
    {'session_id':3,'session_label':'Feb 20 — Exam Tips'},
]

@student_bp.route('/dashboard')
@student_required
def dashboard():
    name = session.get('student_name', 'Student')
    sid  = session.get('student_id',   'STU-001')
    student_info = {
        'full_name':         name,
        'student_id':        sid,
        'class_level':       '10A',
        'section':           'A',
        'performance_index': 85,
        'risk_level':        'low',
        'prediction_count':  3
    }
    return render_template('student/dashboard.html', student=student_info, recs=AI_RECS)

@student_bp.route('/predict', methods=['POST'])
@student_required
def predict():
    term1_score     = float(request.form.get('t1', 0))
    term2_score     = float(request.form.get('t2', 0))
    term3_score     = float(request.form.get('t3', 0))
    attendance_rate = float(request.form.get('attendance', 0))
    subject_name    = request.form.get('subject', '')

    # Placeholder formula — replace with: model.predict([features])
    avg             = (term1_score + term2_score + term3_score) / 3
    att_factor      = attendance_rate / 100
    predicted_score = round(avg * 0.7 + att_factor * 30)
    predicted_score = max(0, min(100, predicted_score))

    if predicted_score >= 75:   risk_level, grade, pi_label = 'low',    'A' if predicted_score>=85 else 'B+', 'Excellent' if predicted_score>=85 else 'Good'
    elif predicted_score >= 55: risk_level, grade, pi_label = 'medium', 'C+', 'Average'
    else:                       risk_level, grade, pi_label = 'high',   'D',  'Below Average'

    result = {
        'predicted_score':  predicted_score,
        'grade':            grade,
        'pi_label':         pi_label,
        'risk_level':       risk_level,
        'confidence_score': 82
    }
    name = session.get('student_name', 'Student')
    sid  = session.get('student_id',   'STU-001')
    student_info = {
        'full_name':         name,
        'student_id':        sid,
        'class_level':       '10A',
        'section':           'A',
        'performance_index': 85,
        'risk_level':        'low',
        'prediction_count':  3
    }
    return render_template('student/dashboard.html', student=student_info, recs=AI_RECS,
                           result=result, subject_name=subject_name)

@student_bp.route('/activity')
@student_required
def activity():
    stats = {
        'total':        len(PREDICTION_HISTORY),
        'high_risk':    sum(1 for p in PREDICTION_HISTORY if p['risk_level']=='high'),
        'avg_score':    round(sum(p['predicted_score'] for p in PREDICTION_HISTORY)/len(PREDICTION_HISTORY)),
        'best_subject': max(PREDICTION_HISTORY, key=lambda p: p['predicted_score'])['subject_name'][:2].upper()
    }
    return render_template('student/activity.html', history=PREDICTION_HISTORY, stats=stats)

@student_bp.route('/chatbot')
@student_required
def chatbot():
    name = session.get('student_name', 'Student')
    sid  = session.get('student_id',   'STU-001')
    return render_template('student/chatbot.html',
                           student_name=name, student_id=sid,
                           chat_session=CHAT_SESSION)

@student_bp.route('/chatbot/send', methods=['POST'])
@student_required
def chatbot_send():
    msg = request.json.get('message', '')
    msg_lower = msg.lower()
    if 'science' in msg_lower or 'improve' in msg_lower:
        reply = 'Based on your Science academic_record:\n• predicted_score: 52% (Below Average)\n• attendance_rate: 80%\n\nRecommendations:\n1. Attend all practical sessions\n2. Review chapters 5–7 on Chemical Reactions\n3. Form a study group with high-performers'
    elif 'risk' in msg_lower:
        reply = 'Your current overall risk_level is LOW ✓\nperformance_index: 85% (above school avg 84%)\nGrade: A-\n\nWatch out for:\n⚠ Science — HIGH RISK (predicted_score: 52%)\n⚠ History — attendance_rate at 70%'
    elif 'pi' in msg_lower or 'performance' in msg_lower:
        reply = 'Your performance_index is calculated using:\n• term1_score (20%)\n• term2_score (30%)\n• term3_score (30%)\n• attendance_rate (20%)\n\nYour current performance_index: 85%'
    else:
        reply = f'Let me check your academic profile for: "{msg}". Analyzing your records...'
    return jsonify({'reply': reply})
