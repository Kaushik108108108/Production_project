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

# ── Mock prediction history ──
PREDICTION_HISTORY = [
    {'id':'PRD-001','date':'Mar 01, 2026','subject':'Mathematics',    'score':75,'pi':'Good',        'risk':'low',   'rec':'Maintain current study habits and review weekly.'},
    {'id':'PRD-002','date':'Feb 18, 2026','subject':'Science',        'score':52,'pi':'Below Average','risk':'high',  'rec':'Focus on practical experiments, attend extra sessions.'},
    {'id':'PRD-003','date':'Jan 30, 2026','subject':'English',        'score':88,'pi':'Excellent',    'risk':'low',   'rec':'Continue reading widely. Explore creative writing.'},
    {'id':'PRD-004','date':'Jan 15, 2026','subject':'History',        'score':61,'pi':'Average',      'risk':'medium','rec':'Review key events. Improve attendance urgently.'},
    {'id':'PRD-005','date':'Dec 20, 2025','subject':'Computer Science','score':92,'pi':'Excellent',   'risk':'low',   'rec':'Outstanding. Consider competitions.'},
]

AI_RECS = [
    {'subject':'Mathematics',  'tip':'Focus on algebra. Chapters 3–4 need review. Attendance below threshold.',       'type':'warning'},
    {'subject':'Science',      'tip':'Strong performance. Consider advanced practical experiments to boost further.',  'type':'success'},
    {'subject':'History',      'tip':'URGENT: Attendance at 70%. Risk of exam disqualification if not improved.',     'type':'danger'},
    {'subject':'English',      'tip':'Excellent. Continue reading widely and expand essay writing practice.',          'type':'success'},
]

CHAT_HISTORY = [
    {'id':1,'label':'Today — Study Advice'},
    {'id':2,'label':'Mar 05 — Science Review'},
    {'id':3,'label':'Feb 20 — Exam Tips'},
]

# ────────────────────────────────────────────────────────────
@student_bp.route('/dashboard')
@student_required
def dashboard():
    name = session.get('student_name', 'Student')
    sid  = session.get('student_id',   'STU-001')
    student_info = {'name': name, 'id': sid, 'cls': '10A', 'sec': 'A', 'pi': 85, 'risk': 'low', 'predictions': 3}
    return render_template('student/dashboard.html', student=student_info, recs=AI_RECS)

@student_bp.route('/predict', methods=['POST'])
@student_required
def predict():
    """Run prediction — wire to ML model later"""
    t1      = float(request.form.get('t1', 0))
    t2      = float(request.form.get('t2', 0))
    t3      = float(request.form.get('t3', 0))
    att     = float(request.form.get('attendance', 0))
    subject = request.form.get('subject', '')

    # Placeholder formula — replace with trained model: model.predict(features)
    avg        = (t1 + t2 + t3) / 3
    att_factor = att / 100
    predicted  = round(avg * 0.7 + att_factor * 30)
    predicted  = max(0, min(100, predicted))

    if predicted >= 75:   risk, grade, pi = 'low',    'A' if predicted>=85 else 'B+', 'Excellent' if predicted>=85 else 'Good'
    elif predicted >= 55: risk, grade, pi = 'medium', 'C+', 'Average'
    else:                 risk, grade, pi = 'high',   'D',  'Below Average'

    result = {'predicted': predicted, 'grade': grade, 'pi_label': pi, 'risk': risk, 'confidence': 82}
    name   = session.get('student_name', 'Student')
    sid    = session.get('student_id',   'STU-001')
    student_info = {'name': name, 'id': sid, 'cls': '10A', 'sec': 'A', 'pi': 85, 'risk': 'low', 'predictions': 3}
    return render_template('student/dashboard.html', student=student_info, recs=AI_RECS,
                           result=result, subject=subject)

@student_bp.route('/activity')
@student_required
def activity():
    stats = {
        'total': len(PREDICTION_HISTORY),
        'high':  sum(1 for p in PREDICTION_HISTORY if p['risk']=='high'),
        'avg':   round(sum(p['score'] for p in PREDICTION_HISTORY)/len(PREDICTION_HISTORY)),
        'best':  max(PREDICTION_HISTORY, key=lambda p: p['score'])['subject'][:2].upper()
    }
    return render_template('student/activity.html', history=PREDICTION_HISTORY, stats=stats)

@student_bp.route('/chatbot')
@student_required
def chatbot():
    name = session.get('student_name', 'Student')
    sid  = session.get('student_id',   'STU-001')
    return render_template('student/chatbot.html',
                           student_name=name, student_id=sid,
                           chat_history=CHAT_HISTORY)

@student_bp.route('/chatbot/send', methods=['POST'])
@student_required
def chatbot_send():
    msg = request.json.get('message', '')
    msg_lower = msg.lower()
    if 'science' in msg_lower or 'improve' in msg_lower:
        reply = 'Based on your Science records:\n• Predicted score: 52% (Below Average)\n• Attendance: 80%\n\nRecommendations:\n1. Attend all practical sessions — 30% weightage\n2. Review chapters 5–7 on Chemical Reactions\n3. Form a study group with high-performers'
    elif 'risk' in msg_lower:
        reply = 'Your current overall risk level is LOW ✓\nPerformance Index: 85% (above school avg 84%)\nGrade: A-\n\nWatch out for:\n⚠ Science — HIGH RISK (52% predicted)\n⚠ History — attendance at 70%'
    elif 'pi' in msg_lower or 'calculated' in msg_lower:
        reply = 'Your Performance Index (PI) is calculated using:\n• Term 1 Score (20%)\n• Term 2 Score (30%)\n• Term 3 Score (30%)\n• Attendance Rate (20%)\n\nYour current PI: 85%'
    else:
        reply = f'Let me check your academic profile for: "{msg}".\nAnalyzing your records to provide a personalised answer...'
    return jsonify({'reply': reply})
