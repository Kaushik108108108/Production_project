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
    {'prediction_id':'PRD-001','created_at':'Mar 01, 2026','subject_name':'Mathematics',    'term1_score':72,'term2_score':68,'term3_score':65,'attendance_rate':68,'predicted_score':75,'grade':'B+','performance_index':'Good',        'risk_level':'low',   'trend_label':'↓ Declining', 'ai_recommendation':'Maintain current study habits and review weekly.'},
    {'prediction_id':'PRD-002','created_at':'Feb 18, 2026','subject_name':'Science',        'term1_score':50,'term2_score':48,'term3_score':45,'attendance_rate':72,'predicted_score':52,'grade':'F', 'performance_index':'Below Average','risk_level':'high',  'trend_label':'↓ Declining', 'ai_recommendation':'Focus on practical experiments, attend extra sessions.'},
    {'prediction_id':'PRD-003','created_at':'Jan 30, 2026','subject_name':'English',        'term1_score':82,'term2_score':85,'term3_score':88,'attendance_rate':90,'predicted_score':88,'grade':'A', 'performance_index':'Excellent',    'risk_level':'low',   'trend_label':'↑ Improving', 'ai_recommendation':'Continue reading widely. Explore creative writing.'},
    {'prediction_id':'PRD-004','created_at':'Jan 15, 2026','subject_name':'History',        'term1_score':65,'term2_score':62,'term3_score':60,'attendance_rate':70,'predicted_score':61,'grade':'C+','performance_index':'Average',      'risk_level':'medium','trend_label':'↓ Declining', 'ai_recommendation':'Review key events. Improve attendance urgently.'},
    {'prediction_id':'PRD-005','created_at':'Dec 20, 2025','subject_name':'Computer Science','term1_score':88,'term2_score':90,'term3_score':93,'attendance_rate':92,'predicted_score':92,'grade':'A', 'performance_index':'Excellent',   'risk_level':'low',   'trend_label':'↑ Improving', 'ai_recommendation':'Outstanding. Consider competitions.'},
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

# ── HELPER: Trend Analysis ──
def calculate_trend(term1_score, term2_score, term3_score):
    diff1 = term2_score - term1_score
    diff2 = term3_score - term2_score
    if diff1 > 3 and diff2 > 3:
        return 'improving',  '↑ Improving',  'You are consistently improving each term. Keep it up!'
    elif diff1 < -3 and diff2 < -3:
        return 'declining',  '↓ Declining',  'Your marks are dropping each term. Seek help immediately.'
    elif diff1 > 3 and diff2 < -3:
        return 'unstable',   '~ Unstable',   'Marks went up then dropped. Try to maintain consistency.'
    elif diff1 < -3 and diff2 > 3:
        return 'recovering', '↑ Recovering', 'Marks dropped in term 2 but you recovered in term 3. Well done!'
    else:
        return 'stable',     '→ Stable',     'Performance is consistent across all terms.'

# ── HELPER: Grade ──
def get_grade(score):
    if score >= 85:   return 'A'
    elif score >= 75: return 'B+'
    elif score >= 65: return 'B'
    elif score >= 55: return 'C+'
    elif score >= 45: return 'C'
    else:             return 'F'

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
        'prediction_count':  len(PREDICTION_HISTORY)
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

    # ── STEP 1: Predict final score from academic data only ──
    # TODO: replace with → predicted_score = score_model.predict([[t1,t2,t3,att]])[0]
    score_avg       = (term1_score + term2_score + term3_score) / 3
    att_factor      = (attendance_rate / 100) * 25
    predicted_score = round((score_avg * 0.75) + att_factor)
    predicted_score = max(0, min(100, predicted_score))

    # ── STEP 1.5: Trend Analysis ──
    trend, trend_label, trend_note = calculate_trend(term1_score, term2_score, term3_score)

    # ── STEP 2: Risk from predicted score only (student has no complaint/dues input) ──
    # TODO: replace with → risk_level = risk_model.predict([[predicted_score,att,0,0]])[0]
    if predicted_score >= 75:   risk_level, pi_label = 'low',    'Excellent' if predicted_score>=85 else 'Good'
    elif predicted_score >= 55: risk_level, pi_label = 'medium', 'Average'
    else:                       risk_level, pi_label = 'high',   'Below Average'

    # Declining trend escalates risk
    if trend == 'declining' and risk_level == 'low':
        risk_level = 'medium'
    elif trend == 'declining' and risk_level == 'medium':
        risk_level = 'high'

    grade = get_grade(predicted_score)

    result = {
        'predicted_score':  predicted_score,
        'grade':            grade,
        'pi_label':         pi_label,
        'risk_level':       risk_level,
        'confidence_score': 82,
        'trend':            trend,
        'trend_label':      trend_label,
        'trend_note':       trend_note,
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
        'prediction_count':  len(PREDICTION_HISTORY)
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
        reply = 'Based on your Science records:\n• Predicted score: 52% (Below Average)\n• Attendance rate: 72%\n• Trend: Declining ↓\n\nRecommendations:\n1. Attend all practical sessions\n2. Review chapters 5–7 on Chemical Reactions\n3. Form a study group with high-performers'
    elif 'risk' in msg_lower:
        reply = 'Your current overall risk level is LOW ✓\nPerformance Index: 85%\nGrade: A-\n\nWatch out for:\n⚠ Science — HIGH RISK (predicted: 52%)\n⚠ History — attendance at 70%, Declining trend'
    elif 'trend' in msg_lower:
        reply = 'Your trend analysis:\n↑ Improving: English, Computer Science\n↓ Declining: Mathematics, Science, History\n→ Stable: Geography, Physical Education\n\nFocus on the declining subjects immediately.'
    elif 'pi' in msg_lower or 'performance' in msg_lower:
        reply = 'Your Performance Index is calculated using:\n• Term 1 Score (25%)\n• Term 2 Score (25%)\n• Term 3 Score (25%)\n• Attendance Rate (25%)\n\nYour current PI: 85%'
    else:
        reply = f'Let me check your academic profile for: "{msg}". Analyzing your records...'
    return jsonify({'reply': reply})
