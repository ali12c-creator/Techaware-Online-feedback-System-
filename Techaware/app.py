from flask import Flask, request, jsonify, render_template, send_file, session, redirect, url_for, flash
from textblob import TextBlob
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
from functools import wraps
import os
from dotenv import load_dotenv
load_dotenv()
import secrets
import string
import bcrypt
from itsdangerous import URLSafeTimedSerializer
import google.generativeai as genai
from apscheduler.schedulers.background import BackgroundScheduler
from google.api_core.exceptions import GoogleAPIError

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print(f"✅ Gemini AI configured!")
    except Exception as e:
        print(f"❌ Gemini error: {e}")

def analyze_with_gemini(feedback_texts):
    def _empty(summary, suggestions):
        return {
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'overall_sentiment': 'neutral',
            'summary': summary,
            'suggestions': suggestions,
            'strengths': [],
            'areas_to_improve': []
        }
    
    if not feedback_texts:
        return _empty(
            'No feedback received yet',
            ['Encourage students to give feedback']
        )
    
    # Use hardcoded key directly
    api_key = 'AIzaSyCKFE5yEUEA5Kiv4PVvvATV5BKlF92FXQ8'
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        combined = "\n".join([
            f"Student {i+1}: {t}" 
            for i, t in enumerate(feedback_texts)
        ])
        
        prompt = f"""
Analyze these student feedbacks for a university teacher.
Return ONLY valid JSON, no markdown, no extra text:

Feedbacks:
{combined}

Return exactly this JSON structure:
{{
    "positive_count": 0,
    "negative_count": 0,
    "neutral_count": 0,
    "overall_sentiment": "neutral",
    "summary": "summary here",
    "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
    "strengths": ["strength 1", "strength 2"],
    "areas_to_improve": ["area 1", "area 2"]
}}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = text.replace('```json','').replace('```','').strip()
        import json
        result = json.loads(text)
        print(f"✅ Gemini AI analysis successful!")
        return result
        
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return _empty(
            'AI analysis temporarily unavailable',
            [
                'Use more real-world examples',
                'Slow down lecture pace',
                'Ask students for questions'
            ]
        )


def get_current_teacher_from_session():
    from models import Teacher

    teacher_email = session.get('email')
    if not teacher_email:
        return None

    return Teacher.query.filter_by(email=teacher_email).first()

def send_student_feedback_email(student_email,
    student_name, teacher_name, subject_name,
    feedback_url, class_time):
    
    msg = MIMEMultipart('alternative')
    msg['From'] = SENDER_EMAIL
    msg['To'] = student_email
    msg['Subject'] = f"📝 Feedback Required - {subject_name}"
    
    html_body = f"""
<div style='font-family:Arial,sans-serif;max-width:600px;margin:auto;background:#f9f9f9;padding:30px;border-radius:12px'>
    
    <div style='text-align:center;margin-bottom:30px'>
        <h1 style='color:#6C63FF;margin:0'>TechAware</h1>
        <p style='color:#888;margin:5px 0'>Smart Feedback System</p>
    </div>

    <div style='background:white;padding:25px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08)'>
        <h2 style='color:#333;margin-top:0'>Assalam o Alaikum, {student_name}! 👋</h2>
        
        <p style='color:#555;font-size:16px'>
            Aaj aapka <b style='color:#6C63FF'>{subject_name}</b> lecture khatam hua.<br>
            <b>{teacher_name}</b> aapki feedback ka intezaar kar rahe hain!
        </p>

        <p style='color:#555;font-size:15px'>
            Apna feedback dene ke liye neeche button click karein —
            aap seedha apne <b>Student Portal</b> pe pohonch jaenge.
        </p>

        <div style='text-align:center;margin:30px 0'>
            <a href='{feedback_url}'
               style='background:#6C63FF;color:white;padding:14px 35px;
                      border-radius:8px;text-decoration:none;font-size:16px;
                      font-weight:bold;display:inline-block'>
                🌟 Feedback Dene Ke Liye Click Karein
            </a>
        </div>

        <p style='color:#aaa;font-size:13px;text-align:center'>
            Yeh link sirf aaj ke liye valid hai.<br>
            Agar button kaam na kare to yeh link copy karein:<br>
            <a href='{feedback_url}' style='color:#6C63FF'>{feedback_url}</a>
        </p>
    </div>

    <p style='color:#ccc;font-size:12px;text-align:center;margin-top:20px'>
        TechAware Automated System — Please do not reply to this email.
    </p>
</div>"""
    
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {student_email}")
    except (smtplib.SMTPException, OSError) as e:
        print(f"Email error: {e}")

def check_and_send_feedback_emails():
    with app.app_context():
        from models import Timetable, Student, Teacher
        
        now = datetime.now()
        current_weekday = now.weekday()
        current_time = now.time().replace(
            second=0, microsecond=0)
        
        print(f"Checking lectures: {now.strftime('%H:%M')} weekday={current_weekday}")
        
        timetables = Timetable.query.all()
        
        for tt in timetables:
            if tt.day_of_week != current_weekday:
                continue
            
            if not tt.end_time:
                continue
                
            tt_end = tt.end_time.replace(
                second=0, microsecond=0)
            
            if tt_end != current_time:
                continue
            
            print(f"Lecture ended! Sending emails...")
            
            teacher = Teacher.query.get(tt.teacher_id)
            
            # Find tokens for this timetable 
            # that haven't been emailed yet
            sent_tokens = set()
            tokens_to_send = []
            for token, data in feedback_tokens.items():
                if (int(data.get('timetable_id', 0)) == tt.id
                        and not data.get('email_sent', False)
                        and token not in sent_tokens):
                    tokens_to_send.append((token, data))
                    sent_tokens.add(token)
            
            for token, token_data in tokens_to_send:
                student = Student.query.get(
                    token_data['student_id'])
                
                if student and student.email:
                    base_url = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')
                    feedback_url = f"{base_url}/feedback/{token}"
                    
                    send_student_feedback_email(
                        student_email=student.email,
                        student_name=student.name,
                        teacher_name=teacher.name if teacher else "Teacher",
                        subject_name="Lecture",
                        feedback_url=feedback_url,
                        class_time=now.strftime('%H:%M')
                    )
                    
                    # Mark as sent
                    feedback_tokens[token]['email_sent'] = True
                    
                    print(f"Email sent to {student.email}")

def send_teacher_daily_summary():
    from models import Teacher, Feedback, SystemSettings, db
    from datetime import date, datetime

    with app.app_context():
        summary_time_str = SystemSettings.get('summary_email_time', '19:00')
        now = datetime.now()
        current_time_str = now.strftime('%H:%M')

        try:
            summary_dt = datetime.strptime(summary_time_str, '%H:%M').replace(
                year=now.year, month=now.month, day=now.day)
            diff = abs((now - summary_dt).total_seconds())
            if diff > 90:
                return
        except Exception:
            if current_time_str != summary_time_str:
                return
        print(f"Summary time matched! Sending teacher emails...")

        today = date.today()
        teachers = Teacher.query.all()

        for teacher in teachers:
            if not teacher.email:
                continue

            feedbacks = Feedback.query.filter(
                Feedback.teacher_id == teacher.id
            ).all()
            print(f"Teacher {teacher.name}: {len(feedbacks)} feedbacks found")

            total = len(feedbacks)
            avg_rating = round(
                sum(f.rating_overall for f in feedbacks if f.rating_overall) /
                max(1, sum(1 for f in feedbacks if f.rating_overall)), 1
            )

            feedback_rows = ""
            for f in feedbacks:
                feedback_rows += f"""
                <tr>
                    <td style='padding:8px;border:1px solid #ddd'>{f.student_name}</td>
                    <td style='padding:8px;border:1px solid #ddd'>{f.feedback_text[:100]}...</td>
                    <td style='padding:8px;border:1px solid #ddd'>{f.rating_overall or 'N/A'}/5</td>
                    <td style='padding:8px;border:1px solid #ddd'>{f.sentiment}</td>
                </tr>"""

            teacher_portal_url = os.environ.get('BASE_URL', 'http://127.0.0.1:5000') + '/teacher/dashboard'

            html_body = f"""
            <div style='font-family:Arial,sans-serif;max-width:600px;margin:auto;background:#f9f9f9;padding:30px;border-radius:12px'>
    
    <div style='text-align:center;margin-bottom:30px'>
        <h1 style='color:#6C63FF;margin:0'>TechAware</h1>
        <p style='color:#888;margin:5px 0'>Smart Feedback System</p>
    </div>

    <div style='background:white;padding:25px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08)'>
        <h2 style='color:#333;margin-top:0'>Assalam o Alaikum, {teacher.name}! 📊</h2>

        <p style='color:#555;font-size:16px'>
            Aaj <b style='color:#6C63FF'>{total}</b> students ne feedback di hai.
        </p>

        <p style='color:#555;font-size:15px'>
            Apne portal pe ja ke poori detail dekhein —
            ratings, sentiments, aur har student ka feedback.
        </p>

        <div style='background:#f0eeff;padding:15px;border-radius:8px;margin:20px 0;text-align:center'>
            <p style='margin:0;color:#6C63FF;font-size:15px'>
                ⭐ Average Rating: <b>{avg_rating}/5</b> &nbsp;|&nbsp;
                💬 Total Feedback: <b>{total}</b>
            </p>
        </div>

        <div style='text-align:center;margin:25px 0'>
            <a href='{teacher_portal_url}'
               style='background:#6C63FF;color:white;padding:14px 35px;
                      border-radius:8px;text-decoration:none;font-size:16px;
                      font-weight:bold;display:inline-block'>
                📊 Feedback Dashboard Dekhein
            </a>
        </div>

        <p style='color:#aaa;font-size:13px;text-align:center'>
            Agar button kaam na kare to yeh link copy karein:<br>
            <a href='{teacher_portal_url}' style='color:#6C63FF'>{teacher_portal_url}</a>
        </p>
    </div>

    <p style='color:#ccc;font-size:12px;text-align:center;margin-top:20px'>
        TechAware Automated System — Please do not reply to this email.
    </p>
</div>"""

            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = f"TechAware: Today's Feedback Summary — {today.strftime('%d %b %Y')}"
                _mail_user = SENDER_EMAIL
                _mail_pass = SENDER_PASSWORD
                msg['From'] = _mail_user
                msg['To'] = teacher.email
                msg.attach(MIMEText(html_body, 'html'))

                if not _mail_user or not _mail_pass:
                    print(f"Email credentials missing!")
                    continue

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(_mail_user, _mail_pass)
                server.sendmail(_mail_user, teacher.email, msg.as_string())
                server.quit()
                print(f"Summary sent to {teacher.email}")
            except Exception as e:
                print(f"Email error for {teacher.email}: {e}")

app = Flask(__name__)

scheduler = BackgroundScheduler()

scheduler.add_job(
    func=check_and_send_feedback_emails,
    trigger='interval',
    minutes=1,
    id='check_lectures'
)

scheduler.add_job(
    func=send_teacher_daily_summary,
    trigger='interval',
    minutes=1,
    id='daily_summary'
)

scheduler.start()

# Global token storage
feedback_tokens = {}

app.secret_key = os.environ.get('SECRET_KEY', 'techaware-secret-key-change-in-production-2024')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

# ========== EMAIL CONFIGURATION ==========
TEACHER_EMAIL = "hakerbabo01@gmail.com"
SENDER_EMAIL = os.environ.get('MAIL_USERNAME', 'aliahmadobedient479@gmail.com')
SENDER_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

# ========== DATA ==========
feedback_data = {
    "understood": 0,
    "not_understood": 0,
    "neutral": 0,
    "feedback_list": []
}

# ========== USER CREDENTIALS & ROLES = ==========
# In production, use hashed passwords and database storage
users = {
    "admin": {
        "password": "Admin@2024",
        "role": "admin",
        "name": "Administrator"
    },
    "teacher": {
        "password": "teacher123",
        "role": "teacher",
        "name": "Teacher"
    }
}

# ========== AUTHENTICATION DECORATOR ==========
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def student_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session \
           and 'student_id' not in session \
           and 'user_id' not in session:
            return redirect('/login')
        if session.get('role') != 'student':
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def get_role_redirect_url(role):
    role_redirect_map = {
        'admin': '/admin_manage',
        'teacher': '/teacher/dashboard',
        'batch advisor': '/batch_advisor/dashboard',
        'student': '/student/dashboard'
    }
    return role_redirect_map.get(role, '/login')

def role_required(allowed_roles):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session:
                return redirect('/login')
            if session.get('role') not in allowed_roles:
                role = session.get('role')
                if role == 'admin':
                    return redirect('/admin_manage')
                elif role == 'teacher':
                    return redirect('/teacher/dashboard')
                elif role == 'batch advisor':
                    return redirect('/batch_advisor/dashboard')
                elif role == 'student':
                    return redirect('/student/dashboard')
                return redirect('/login')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ========== AI SUGGESTIONS ==========
def generate_ai_suggestions(feedback_text, sentiment):
    suggestions = []
    feedback_lower = feedback_text.lower()
    
    if sentiment == "❌ NOT UNDERSTOOD":
        if any(word in feedback_lower for word in ["fast", "speed", "quick", "rush", "jaldi"]):
            suggestions.append("💡 Slow down the pace and use more examples")
        
        if any(word in feedback_lower for word in ["confusing", "confused", "unclear", "nahi", "samajh"]):
            suggestions.append("💡 Break complex concepts into smaller parts")
        
        if any(word in feedback_lower for word in ["practical", "example", "real"]):
            suggestions.append("💡 Include more real-world examples")
        
        if any(word in feedback_lower for word in ["diagram", "visual", "picture"]):
            suggestions.append("💡 Use more diagrams and visual aids")
        
        if len(suggestions) == 0:
            suggestions.append("💡 Consider using interactive teaching methods")
    
    elif sentiment == "✅ UNDERSTOOD":
        suggestions.append("✨ Great job! Keep this teaching approach")
        if any(word in feedback_lower for word in ["interesting", "engaging", "fun", "acha"]):
            suggestions.append("✨ Continue with engaging techniques")
    
    else:
        suggestions.append("💭 Ask for more specific feedback")
    
    return suggestions


def get_weighted_rating(feedbacks, feedback_tokens):
    if not feedbacks:
        return 0
    
    total_weight = 0
    weighted_sum = 0
    
    for f in feedbacks:
        # Check student attendance
        student_id = f.student_id
        teacher_id = f.teacher_id
        
        # Count total classes for this teacher
        total_classes = len(set([
            t.get('timetable_id') 
            for t in feedback_tokens.values()
            if t.get('timetable_id')
        ]))
        
        # Count student present count
        present_count = len([
            t for t in feedback_tokens.values()
            if t.get('student_id') == student_id
        ])
        
        # Calculate attendance percentage
        if total_classes > 0:
            attendance_pct = present_count / total_classes
        else:
            attendance_pct = 1.0
        
        # Weight based on attendance
        if attendance_pct >= 0.75:
            weight = 1.0    # Full weight
        elif attendance_pct >= 0.50:
            weight = 0.6    # 60% weight
        elif attendance_pct >= 0.25:
            weight = 0.3    # 30% weight
        else:
            weight = 0.1    # 10% weight
        
        if f.rating_overall:
            weighted_sum += f.rating_overall * weight
            total_weight += weight
    
    if total_weight == 0:
        return 0
    return round(weighted_sum / total_weight, 1)

# ========== ROUTES ==========

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/feedback/<token>')
def feedback_with_token(token):
    # Check token exists
    if token not in feedback_tokens:
        return render_template('feedback.html',
            error="Invalid or expired link",
            token_valid=False,
            token=None)
    
    token_data = feedback_tokens[token]
    
    # Check expiry
    if datetime.now() > token_data['expires_at']:
        return render_template('feedback.html',
            error="This link has expired",
            token_valid=False,
            token=None)
    
    # Check already used
    if token_data['used']:
        return render_template('feedback.html',
            error="Feedback already submitted",
            token_valid=False,
            token=None)
    
    from models import Student, Timetable
    student = Student.query.get(token_data['student_id'])
    timetable = Timetable.query.get(
        token_data['timetable_id'])
    
    return render_template('feedback.html',
        token=token,
        token_valid=True,
        student=student,
        timetable=timetable)


@app.route('/feedback')
@student_login_required
def feedback_page():
    return render_template('feedback.html',
        token=None,
        token_valid=True,
        error=None)

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_manage'))
    elif role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif role == 'batch advisor':
        return redirect(url_for('batch_advisor_dashboard'))
    elif role == 'student':
        return redirect(url_for('student_dashboard'))
    return redirect('/login')


@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('dashboard'))
    
    from models import Teacher, Feedback, Timetable
    teacher = get_current_teacher_from_session()
    
    if not teacher:
        return render_template('teacher_dashboard.html',
            user=session,
            teacher=None,
            stats={},
            recent_feedbacks=[],
            timetables=[],
            ai_analysis={}
        )
    
    # Get all feedbacks
    feedbacks = Feedback.query.filter_by(
        teacher_id=teacher.id).all()
    
    # Calculate stats (attendance-weighted average)
    total_feedbacks = len(feedbacks)
    # Use weighted rating by attendance
    avg_rating = get_weighted_rating(feedbacks, feedback_tokens) if feedbacks else 0
    positive = len([f for f in feedbacks if f.sentiment == 'UNDERSTOOD']) if feedbacks else 0
    negative = len([f for f in feedbacks if f.sentiment == 'NOT_UNDERSTOOD']) if feedbacks else 0
    neutral = total_feedbacks - positive - negative
    
    # Get timetables
    timetables = Timetable.query.filter_by(
        teacher_id=teacher.id).all()
    
    # Recent feedbacks (last 5)
    recent_feedbacks = Feedback.query.filter_by(
        teacher_id=teacher.id
    ).order_by(
        Feedback.created_at.desc()
    ).limit(5).all()
    
    stats = {
        'total_feedbacks': total_feedbacks,
        'avg_rating': round(avg_rating, 1),
        'positive': positive,
        'negative': negative,
        'neutral': neutral,
        'total_classes': len(timetables),
        'attendance_pending': max(0, len(timetables) - 1)  # Placeholder: adjust based on actual attendance logic
    }
    
    # Call Gemini API for AI analysis
    feedback_texts = [f.feedback_text for f in feedbacks if f.feedback_text]
    ai_analysis = analyze_with_gemini(feedback_texts)

    return render_template('teacher_dashboard.html',
        user=session,
        teacher=teacher,
        stats=stats,
        recent_feedbacks=recent_feedbacks,
        timetables=timetables,
        ai_analysis=ai_analysis
    )

@app.route('/teacher/attendance')
@app.route('/teacher/mark-attendance')
@login_required
def attendance_page():
    if session.get('role') != 'teacher':
        return redirect('/login')
    
    from models import Teacher, Timetable, Course
    teacher = get_current_teacher_from_session()
    
    timetables = Timetable.query.filter_by(
        teacher_id=teacher.id).all() if teacher else []
    
    return render_template(
        'attendance.html',
        timetables=timetables,
        teacher=teacher
    )

@app.route('/api/teacher/get-students', methods=['POST'])
@login_required
def get_class_students():
    data = request.get_json()
    timetable_id = data.get('timetable_id')
    
    from models import Timetable, Student, Section
    teacher = get_current_teacher_from_session()
    timetable = Timetable.query.get(timetable_id)
    if not timetable or not teacher or timetable.teacher_id != teacher.id:
        return jsonify({'success': False})
    
    students = Student.query.filter_by(
        section_id=timetable.section_id).all()
    
    student_list = [{
        'id': s.id,
        'name': s.name,
        'registration_number': s.registration_number
    } for s in students]
    
    return jsonify({
        'success': True,
        'students': student_list,
        'subject': timetable.subject_name if hasattr(
            timetable, 'subject_name') else 'Class',
        'section': timetable.section_id
    })

@app.route('/api/teacher/mark-attendance', methods=['POST'])
@login_required
def mark_attendance():
    try:
        from models import Student
        import secrets
        from datetime import datetime, timedelta
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data received'
            })
        timetable_id = int(data.get('timetable_id'))
        present_students = data.get(
            'present_students', [])
        absent_students = data.get(
            'absent_students', [])
        
        from models import Timetable as _TimetableLookup
        _tt_lookup = _TimetableLookup.query.filter_by(id=int(timetable_id)).first()
        _teacher = get_current_teacher_from_session()
        if not _tt_lookup or not _teacher or _tt_lookup.teacher_id != _teacher.id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized timetable selection'
            })
        _teacher_id_lookup = _tt_lookup.teacher_id if _tt_lookup else None
        print(f"mark_attendance: timetable_id={timetable_id}, teacher_id={_teacher_id_lookup}")

        for student_id in present_students:
            student = Student.query.get(int(student_id))
            if student:
                token = secrets.token_urlsafe(32)
                feedback_tokens[token] = {
                    'student_id': student.id,
                    'timetable_id': timetable_id,
                    'teacher_id': _teacher_id_lookup,
                    'created_at': datetime.now(),
                    'expires_at': datetime.now() + 
                        timedelta(hours=24),
                    'used': False,
                    'email_sent': False
                }
        
        return jsonify({
            'success': True,
            'message': f'Attendance marked! {len(present_students)} present. Emails will be sent at lecture end time automatically.',
            'emails_sent': []
        })
        
    except Exception as e:
        import traceback
        print(f"Attendance ERROR: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/api/teacher/ai-analysis')
@login_required
def get_ai_analysis():
    from models import Teacher, Feedback
    teacher = get_current_teacher_from_session()
    if not teacher:
        return jsonify({'success': False, 'analysis': analyze_with_gemini([])})
    feedbacks = Feedback.query.filter_by(
        teacher_id=teacher.id).all()
    texts = [f.feedback_text for f in feedbacks if f.feedback_text]
    analysis = analyze_with_gemini(texts)
    return jsonify({'success': True, 'analysis': analysis})


@app.route('/batch_advisor/dashboard')
@login_required
def batch_advisor_dashboard():
    if session.get('role') != 'batch advisor':
        return redirect(url_for('dashboard'))
    
    from models import Teacher, Feedback
    
    teachers = Teacher.query.all()
    teacher_stats = []
    
    for teacher in teachers:
        feedbacks = Feedback.query.filter_by(
            teacher_id=teacher.id).all()
        
        # Use weighted average by attendance
        avg = get_weighted_rating(feedbacks, feedback_tokens)
        
        positive = len([f for f in feedbacks 
            if f.sentiment == 'UNDERSTOOD'])
        
        teacher_stats.append({
            'id': teacher.id,
            'name': teacher.name,
            'email': teacher.email,
            'total_feedbacks': total,
            'avg_rating': round(avg, 1),
            'positive_count': positive,
            'status': 'good' if avg >= 2.5 else 'alert',
            'percentage': round((avg / 5) * 100, 0)
        })
    
    good_teachers_list = [t for t in teacher_stats 
        if t['status'] == 'good']
    alert_teachers_list = [t for t in teacher_stats 
        if t['status'] == 'alert']
    good_teachers_count = len(good_teachers_list)
    alert_teachers_count = len(alert_teachers_list)
    
    return render_template('batch_advisor.html',
        user=session,
        teacher_stats=teacher_stats,
        total_teachers=len(teachers),
        good_teachers=good_teachers_count,
        alert_teachers=alert_teachers_list,
        alert_count=alert_teachers_count
    )


@app.route('/batch_advisor/profile')
@login_required
def batch_advisor_profile():
    if session.get('role') != 'batch advisor':
        return redirect('/login')
    
    from models import User
    user = User.query.filter_by(
        email=session.get('email')).first()
    
    return render_template(
        'advisor_profile.html',
        user=session,
        user_data=user
    )

@app.route('/admin')
def admin_panel():
    return redirect('/login')

@app.route('/login', methods=['GET'])
def login_page():
    if 'role' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect('/admin_manage')
        elif role == 'teacher':
            return redirect('/teacher/dashboard')
        elif role == 'batch advisor':
            return redirect('/batch_advisor/dashboard')
        elif role == 'student':
            return redirect('/student/dashboard')
    return render_template('login.html')

@app.route('/api/unified/login', methods=['POST'])
def unified_login():
    from models import User, Student
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'Email and password required!'
        })
    
    # Check User table first
    user = User.query.filter_by(
        email=email, is_active=True).first()
    
    if user:
        from werkzeug.security import check_password_hash
        password_match = False
        try:
            if user.password_hash.startswith('$2'):
                password_match = bcrypt.checkpw(
                    password.encode('utf-8'),
                    user.password_hash.encode('utf-8'))
            else:
                password_match = check_password_hash(
                    user.password_hash, password)
        except:
            password_match = check_password_hash(
                user.password_hash, password)
        
        if password_match:
            session.clear()
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.name
            session['email'] = user.email
            session.permanent = True
            
            role = user.role
            if role == 'admin':
                url = '/admin_manage'
            elif role == 'teacher':
                url = '/teacher/dashboard'
            elif role == 'batch advisor':
                url = '/batch_advisor/dashboard'
            else:
                url = '/dashboard'
            
            return jsonify({
                'success': True,
                'role': role,
                'redirect_url': url
            })
    
    # Check Student table
    from models import Student
    student = Student.query.filter_by(
        email=email, is_active=True).first()
    
    if student:
        from werkzeug.security import check_password_hash
        try:
            match = check_password_hash(
                student.password_hash, password)
        except:
            match = False
        
        if match:
            session.clear()
            session['student_id'] = student.id
            session['user_id'] = student.id
            session['role'] = 'student'
            session['name'] = student.name
            session['email'] = student.email
            session['reg_number'] = student.registration_number
            session.permanent = True
            
            return jsonify({
                'success': True,
                'role': 'student',
                'redirect_url': '/student/dashboard'
            })

    # Check Teacher table (like Student)
    from models import Teacher
    teacher_user = Teacher.query.filter_by(
        email=email, is_active=True).first()

    if teacher_user and teacher_user.password_hash:
        try:
            from werkzeug.security import check_password_hash
            match = check_password_hash(
                teacher_user.password_hash, password)
        except:
            match = False

        if match:
            session.clear()
            session['teacher_id'] = teacher_user.id
            session['user_id'] = teacher_user.id
            session['role'] = 'teacher'
            session['name'] = teacher_user.name
            session['email'] = teacher_user.email
            session.permanent = True
            return jsonify({
                'success': True,
                'role': 'teacher',
                'redirect_url': '/teacher/dashboard'
            })
    
    return jsonify({
        'success': False,
        'message': 'Invalid email or password!'
    })

@app.route('/admin_manage')
@login_required
def admin_manage():
    if session.get('role') != 'admin':
        return redirect(get_role_redirect_url(session.get('role')))
    return render_template("admin_manage.html", user=session)

# ========== STUDENT ROUTES ==========
@app.route('/student/login')
def student_login_page():
    return redirect('/login')

@app.route('/student/dashboard')
@student_login_required
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(get_role_redirect_url(session.get('role')))
    from models import Student, Feedback, StudentCourse, Timetable, Teacher
    
    student = get_current_student_from_session()
    
    if not student:
        student_id = session.get('student_id')
        if student_id:
            student = Student.query.get(student_id)
    
    if not student:
        return render_template(
            'student_dashboard.html',
            student=session,
            courses=[],
            teachers=[],
            feedback_history=[],
            stats={'total_feedbacks': 0,
                   'avg_rating': 0,
                   'pending': 0}
        )
    
    # Get courses
    enrollments = StudentCourse.query.filter_by(
        student_id=student.id).all()
    courses = []
    for e in enrollments:
        if e.course:
            courses.append({
                'id': e.course.id,
                'name': e.course.name,
                'code': e.course.code
            })
    
    # Get teachers
    teachers = []
    for e in enrollments:
        if e.course:
            tts = Timetable.query.filter_by(
                course_id=e.course.id).all()
            for tt in tts:
                teacher = Teacher.query.get(
                    tt.teacher_id)
                if teacher and not any(
                    t['id'] == teacher.id 
                    for t in teachers):
                    teachers.append({
                        'id': teacher.id,
                        'name': teacher.name,
                        'course': e.course.name
                    })
    
    # Get feedback history
    feedbacks = Feedback.query.filter_by(
        student_id=student.id
    ).order_by(
        Feedback.created_at.desc()
    ).all()
    
    feedback_history = []
    for f in feedbacks:
        clean_text = f.feedback_text or ''
        if '[Theory]' in clean_text:
            clean_text = clean_text.split(
                '[Theory]')[0].strip()
        feedback_history.append({
            'rating': f.rating_overall,
            'text': clean_text,
            'sentiment': f.sentiment,
            'date': f.created_at.strftime(
                '%Y-%m-%d') if f.created_at else 'N/A'
        })
    
    total = len(feedbacks)
    avg = sum(
        f.rating_overall for f in feedbacks 
        if f.rating_overall
    ) / max(total, 1)
    
    stats = {
        'total_feedbacks': total,
        'avg_rating': round(avg, 1),
        'total_courses': len(courses),
        'total_teachers': len(teachers),
        'pending': 0
    }
    
    return render_template(
        'student_dashboard.html',
        student=session,
        student_data=student,
        courses=courses,
        teachers=teachers,
        feedback_history=feedback_history,
        stats=stats
    )

# ========== STUDENT API ROUTES ==========
@app.route('/api/student/login', methods=['POST'])
def student_login():
    from models import Student
    data = request.json
    reg_number = data.get("reg_number", "").strip()
    password = data.get("password", "").strip()
    
    if not reg_number or not password:
        return jsonify({"success": False, "message": "❌ Registration number and password are required!"})
    
    student = Student.query.filter_by(registration_number=reg_number).first()
    
    if student and student.check_password(password) and student.is_active:
        session['student_id'] = student.id
        session['user_id'] = student.registration_number
        session['role'] = 'student'
        session['name'] = student.name
        session['reg_number'] = student.registration_number
        session['section'] = student.section
        session.permanent = True
        
        return jsonify({
            "success": True,
            "message": "✅ Login successful!",
            "student": student.to_dict()
        })
    else:
        return jsonify({"success": False, "message": "❌ Invalid registration number or password!"})

def get_current_student_from_session():
    from models import Student

    student_email = session.get('email')
    if student_email:
        student = Student.query.filter_by(email=student_email).first()
        if student:
            return student

    student_id = session.get('student_id') or session.get('user_id')
    if student_id:
        return Student.query.get(student_id)

    return None

@app.route('/api/student/dashboard/data', methods=['GET'])
@student_login_required
def student_dashboard_data():
    from models import Student, StudentCourse, Course, Teacher, Timetable, Feedback
    from sqlalchemy import func
    
    student = get_current_student_from_session()
    
    if not student:
        return jsonify({"success": False, "message": "Student not found!"})

    student_id = student.id

    def _department_name(course):
        department = getattr(course, 'department', None)
        if department is None:
            return None
        if isinstance(department, str):
            return department
        return getattr(department, 'name', None) or str(department)

    def _student_course_dict(course, reg_course):
        course_dict = course.to_dict()
        course_dict['department'] = _department_name(course)
        course_dict['semester'] = reg_course.semester
        course_dict['section'] = reg_course.section
        return course_dict

    def _student_feedback_dict(feedback):
        feedback_dict = feedback.to_dict()
        course_data = feedback_dict.get('course') or {}
        if course_data:
            course_data['department'] = _department_name(feedback.course) if feedback.course else None
            feedback_dict['course'] = course_data
        teacher_data = feedback_dict.get('teacher') or {}
        if teacher_data:
            feedback_dict['teacher'] = teacher_data
        return feedback_dict
    
    # Get registered courses
    registered_courses = StudentCourse.query.filter_by(student_id=student_id).all()
    courses_data = []
    teachers_data = []
    teacher_ids = set()
    course_ids = []
    
    for reg_course in registered_courses:
        course = reg_course.course
        if course:
            courses_data.append(_student_course_dict(course, reg_course))
            course_ids.append(course.id)

    if course_ids:
        timetables = Timetable.query.filter(
            Timetable.course_id.in_(course_ids)
        ).all()

        for timetable in timetables:
            if timetable.teacher_id in teacher_ids:
                continue

            teacher = Teacher.query.get(timetable.teacher_id)
            if not teacher:
                continue

            teacher_dict = teacher.to_dict()
            teacher_dict['course_code'] = timetable.course.code if timetable.course else None
            teacher_dict['course_name'] = timetable.course.name if timetable.course else None
            teacher_dict['department'] = _department_name(timetable.course) if timetable.course else teacher_dict.get('department')
            teachers_data.append(teacher_dict)
            teacher_ids.add(timetable.teacher_id)
    
    # Get feedback history
    feedbacks = Feedback.query.filter_by(registration_number=student.registration_number).order_by(Feedback.created_at.desc()).all()
    feedback_history = [_student_feedback_dict(fb) for fb in feedbacks]
    
    # Calculate statistics
    total_feedbacks = len(feedback_history)
    pending_feedbacks = 0  # This would be calculated based on completed lectures
    
    # Calculate progress
    from models import db as db_models
    avg_rating = db_models.session.query(func.avg(Feedback.rating_overall)).filter_by(registration_number=student.registration_number).scalar()
    avg_rating = round(avg_rating, 2) if avg_rating else 0
    
    sentiment_counts = db_models.session.query(
        Feedback.sentiment,
        func.count(Feedback.id)
    ).filter_by(registration_number=student.registration_number).group_by(Feedback.sentiment).all()
    
    sentiment_stats = {}
    for sentiment, count in sentiment_counts:
        sentiment_stats[sentiment] = count
    
    return jsonify({
        "success": True,
        "student": {**student.to_dict(), "department": _department_name(student.department) if student.department else None},
        "courses": courses_data,
        "teachers": teachers_data,
        "feedback_history": feedback_history,
        "statistics": {
            "total_courses": len(courses_data),
            "total_teachers": len(teachers_data),
            "total_feedbacks": total_feedbacks,
            "pending_feedbacks": pending_feedbacks,
            "average_rating": avg_rating,
            "sentiment_distribution": sentiment_stats
        }
    })

@app.route('/api/student/feedback/history', methods=['GET'])
@student_login_required
def student_feedback_history():
    from models import Feedback
    student = get_current_student_from_session()

    if not student:
        return jsonify({"success": False, "message": "Student not found!"})
    
    feedbacks = Feedback.query.filter_by(
        registration_number=student.registration_number
    ).order_by(Feedback.created_at.desc()).all()
    
    return jsonify({
        "success": True,
        "feedbacks": [
            {
                **fb.to_dict(),
                "course": {
                    **fb.to_dict().get('course', {}),
                    "department": fb.course.department.name if fb.course and fb.course.department else None
                } if fb.to_dict().get('course') else None
            }
            for fb in feedbacks
        ]
    })

@app.route('/api/student/logout', methods=['POST'])
def student_logout():
    session.clear()
    return jsonify({"success": True, "message": "✅ Logged out successfully!"})

# ========== LOGIN/LOGOUT ==========
@app.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.json
    # Accept both 'email' and 'username' for backward compatibility
    email = data.get("email", "").strip() or data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    # DEBUG: Print input email
    print(f"Debug: Input Email is: {email}")
    
    # Try database first - Query by EMAIL
    from models import User
    user = User.query.filter_by(email=email).first()
    
    # DEBUG: Check if user found
    if user:
        print(f"Debug: User found in DB? Yes (ID: {user.id}, Name: {user.name}, Email: {user.email}, Username: {user.username})")
    else:
        print("Debug: User found in DB? No")
        # Try querying by username as fallback for backward compatibility
        user = User.query.filter_by(username=email).first()
        if user:
            print(f"Debug: User found by username? Yes (ID: {user.id}, Name: {user.name}, Email: {user.email}, Username: {user.username})")
    
    if user and user.is_active:
        # Check password - Support both bcrypt and werkzeug hashes
        password_match = False
        
        # Check if password_hash is bcrypt (starts with $2a$, $2b$, or $2y$)
        if user.password_hash.startswith('$2'):
            # Use bcrypt to verify
            try:
                password_bytes = password.encode('utf-8')
                hash_bytes = user.password_hash.encode('utf-8')
                password_match = bcrypt.checkpw(password_bytes, hash_bytes)
                print(f"Debug: Password match? {'Yes' if password_match else 'No'} (using bcrypt)")
            except Exception as e:
                print(f"Debug: Bcrypt check error: {str(e)}")
                password_match = False
        else:
            # Use werkzeug's check_password_hash for old passwords
            from werkzeug.security import check_password_hash
            password_match = check_password_hash(user.password_hash, password)
            print(f"Debug: Password match? {'Yes' if password_match else 'No'} (using werkzeug)")
        
        if password_match:
            session['user_id'] = user.username
            session['role'] = user.role
            session['name'] = user.name
            session.permanent = True
            
            return jsonify({
                "success": True, 
                "message": "✅ Login successful!",
                "role": user.role,
                "name": user.name,
                "redirect_url": get_role_redirect_url(user.role)
            })
        else:
            print("Debug: Password verification failed")
    else:
        if not user:
            print("Debug: User not found or inactive")
    
    # Fallback to hardcoded users (for backward compatibility)
    if email in users and users[email]["password"] == password:
        print(f"Debug: Using hardcoded user: {email}")
        session['user_id'] = email
        session['role'] = users[email]["role"]
        session['name'] = users[email]["name"]
        session.permanent = True
        
        return jsonify({
            "success": True, 
            "message": "✅ Login successful!",
            "role": users[email]["role"],
            "name": users[email]["name"],
            "redirect_url": get_role_redirect_url(users[email]["role"])
        })
    else:
        print("Debug: Login failed - Invalid credentials")
        return jsonify({"success": False, "message": "❌ Invalid email or password!"})

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('admin_panel'))

@app.route('/check_auth', methods=['GET'])
def check_auth():
    if 'user_id' in session and 'role' in session:
        return jsonify({
            "authenticated": True,
            "user_id": session.get('user_id'),
            "role": session.get('role'),
            "name": session.get('name')
        })
    return jsonify({"authenticated": False})

# ========== PASSWORD MANAGEMENT ==========

# Initialize token serializer
def get_serializer():
    return URLSafeTimedSerializer(app.secret_key)

# Helper function to send password reset email
def send_password_reset_email(email, token, user_name):
    """Send password reset email with token link"""
    global smtp_config, SENDER_EMAIL, SENDER_PASSWORD
    
    try:
        reset_url = url_for('reset_password', token=token, _external=True)
        subject = "TechAware - Password Reset Request"
        
        body = f"""Hello {user_name},

You have requested to reset your password for your TechAware account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour for security reasons.

If you did not request this password reset, please ignore this email.

Best regards,
TechAware Feedback System
"""
        
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        # Use SMTP configuration
        try:
            smtp_server = smtp_config['server']
            smtp_port = smtp_config['port']
            smtp_use_tls = smtp_config['use_tls']
            smtp_email = smtp_config['email']
            smtp_password = smtp_config['password']
        except (KeyError, NameError):
            # Fallback to direct configuration
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            smtp_use_tls = True
            smtp_email = SENDER_EMAIL
            smtp_password = SENDER_PASSWORD
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        if smtp_use_tls:
            server.starttls()
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, email, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return False

# Task 1: Forgot Password Route (Public)
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'GET':
        return render_template('forgot_password.html')
    
    # POST request - process forgot password
    from models import User, Student, db
    
    data = request.get_json() if request.is_json else request.form
    email = data.get('email', '').strip()
    
    if not email:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ Email is required!"}), 400
        flash("❌ Email is required!", "error")
        return render_template('forgot_password.html')
    
    # Check in User table (Teachers/Admins)
    user = User.query.filter_by(email=email).first()
    user_type = "user"
    
    # If not found, check in Student table
    if not user:
        student = Student.query.filter_by(email=email).first()
        if student:
            user = student
            user_type = "student"
    
    # Always return success message (security best practice - don't reveal if email exists)
    success_message = "✅ If an account with that email exists, a password reset link has been sent."
    
    if user and user.is_active:
        try:
            # Generate secure token
            serializer = get_serializer()
            token = serializer.dumps(email, salt='password-reset-salt')
            
            # Send email
            user_name = user.name if hasattr(user, 'name') else "User"
            email_sent = send_password_reset_email(email, token, user_name)
            
            if email_sent:
                if request.is_json:
                    return jsonify({"success": True, "message": success_message})
                flash(success_message, "success")
            else:
                if request.is_json:
                    return jsonify({"success": False, "message": "❌ Failed to send email. Please try again later."}), 500
                flash("❌ Failed to send email. Please try again later.", "error")
        except Exception as e:
            print(f"Error generating reset token: {str(e)}")
            if request.is_json:
                return jsonify({"success": False, "message": "❌ Error processing request. Please try again."}), 500
            flash("❌ Error processing request. Please try again.", "error")
    else:
        # Still return success (security - don't reveal if email exists)
        if request.is_json:
            return jsonify({"success": True, "message": success_message})
        flash(success_message, "info")
    
    if request.is_json:
        return jsonify({"success": True, "message": success_message})
    return render_template('forgot_password.html')

# Task 1: Reset Password Route (Public)
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token validation"""
    from models import User, Student, db
    
    serializer = get_serializer()
    
    # Validate token
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hour expiry
    except Exception as e:
        print(f"Token validation error: {str(e)}")
        flash("❌ Invalid or expired reset link. Please request a new one.", "error")
        return render_template('reset_password.html', valid=False, error="Invalid or expired token")
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    user_type = "user"
    
    if not user:
        user = Student.query.filter_by(email=email).first()
        if user:
            user_type = "student"
    
    if not user:
        flash("❌ User not found.", "error")
        return render_template('reset_password.html', valid=False, error="User not found")
    
    if request.method == 'GET':
        return render_template('reset_password.html', valid=True, token=token, email=email)
    
    # POST request - process password reset
    data = request.get_json() if request.is_json else request.form
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    # Validation
    if not new_password or not confirm_password:
        error_msg = "❌ Both password fields are required!"
        if request.is_json:
            return jsonify({"success": False, "message": error_msg}), 400
        flash(error_msg, "error")
        return render_template('reset_password.html', valid=True, token=token, email=email)
    
    if new_password != confirm_password:
        error_msg = "❌ Passwords do not match!"
        if request.is_json:
            return jsonify({"success": False, "message": error_msg}), 400
        flash(error_msg, "error")
        return render_template('reset_password.html', valid=True, token=token, email=email)
    
    if len(new_password) < 6:
        error_msg = "❌ Password must be at least 6 characters long!"
        if request.is_json:
            return jsonify({"success": False, "message": error_msg}), 400
        flash(error_msg, "error")
        return render_template('reset_password.html', valid=True, token=token, email=email)
    
    try:
        # Hash new password with bcrypt
        password_bytes = new_password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt)
        
        # Update password
        user.password_hash = password_hash.decode('utf-8')
        db.session.commit()
        
        success_msg = "✅ Password reset successfully! You can now login with your new password."
        if request.is_json:
            return jsonify({"success": True, "message": success_msg})
        flash(success_msg, "success")
        return redirect(url_for('admin_panel'))
    except Exception as e:
        db.session.rollback()
        print(f"Error resetting password: {str(e)}")
        error_msg = "❌ Error resetting password. Please try again."
        if request.is_json:
            return jsonify({"success": False, "message": error_msg}), 500
        flash(error_msg, "error")
        return render_template('reset_password.html', valid=True, token=token, email=email)

# Task 2: Change Password Route (Protected)
@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Allow logged-in users to change their password"""
    from models import User, Student, db
    
    if request.method == 'GET':
        return render_template('change_password.html')
    
    # POST request - process password change
    data = request.get_json() if request.is_json else request.form
    current_password = data.get('current_password', '').strip()
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    # Validation
    if not current_password or not new_password or not confirm_password:
        error_msg = "❌ All password fields are required!"
        if request.is_json:
            return jsonify({"success": False, "message": error_msg}), 400
        flash(error_msg, "error")
        return render_template('change_password.html')
    
    if new_password != confirm_password:
        error_msg = "❌ New passwords do not match!"
        if request.is_json:
            return jsonify({"success": False, "message": error_msg}), 400
        flash(error_msg, "error")
        return render_template('change_password.html')
    
    if len(new_password) < 6:
        error_msg = "❌ New password must be at least 6 characters long!"
        if request.is_json:
            return jsonify({"success": False, "message": error_msg}), 400
        flash(error_msg, "error")
        return render_template('change_password.html')
    
    if current_password == new_password:
        error_msg = "❌ New password must be different from current password!"
        if request.is_json:
            return jsonify({"success": False, "message": error_msg}), 400
        flash(error_msg, "error")
        return render_template('change_password.html')
    
    # Get user based on role
    user = None
    role = session.get('role')
    user_id = session.get('user_id')
    
    if role == 'student':
        user = Student.query.filter_by(registration_number=user_id).first()
    else:
        # For teachers/admins
        user = User.query.filter_by(username=user_id).first()
        if not user:
            user = User.query.filter_by(email=user_id).first()
    
    if not user:
        error_msg = "❌ User not found!"
        if request.is_json:
            return jsonify({"success": False, "message": error_msg}), 404
        flash(error_msg, "error")
        return render_template('change_password.html')
    
    # Verify current password
    password_match = False
    
    # Check if password_hash is bcrypt (starts with $2a$, $2b$, or $2y$)
    if user.password_hash.startswith('$2'):
        # Use bcrypt to verify
        try:
            password_bytes = current_password.encode('utf-8')
            hash_bytes = user.password_hash.encode('utf-8')
            password_match = bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception as e:
            print(f"Bcrypt check error: {str(e)}")
            password_match = False
    else:
        # Use werkzeug's check_password_hash for old passwords
        from werkzeug.security import check_password_hash
        password_match = check_password_hash(user.password_hash, current_password)
    
    if not password_match:
        error_msg = "❌ Current password is incorrect!"
        if request.is_json:
            return jsonify({"success": False, "message": error_msg}), 401
        flash(error_msg, "error")
        return render_template('change_password.html')
    
    # Update password
    try:
        # Hash new password with bcrypt
        password_bytes = new_password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt)
        
        user.password_hash = password_hash.decode('utf-8')
        db.session.commit()
        
        success_msg = "✅ Password changed successfully!"
        if request.is_json:
            return jsonify({"success": True, "message": success_msg})
        flash(success_msg, "success")
        
        # Redirect based on role
        if role == 'student':
            return redirect(url_for('student_dashboard'))
        else:
            return redirect(url_for('admin_manage'))
    except Exception as e:
        db.session.rollback()
        print(f"Error changing password: {str(e)}")
        error_msg = "❌ Error changing password. Please try again."
        if request.is_json:
            return jsonify({"success": False, "message": error_msg}), 500
        flash(error_msg, "error")
        return render_template('change_password.html')

# ========== SUBMIT FEEDBACK ==========
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    global feedback_data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    if not data:
        return jsonify({'success': False, 'message': 'No data received'}), 400

    token = data.get('token', '')
    if token and token in feedback_tokens:
        feedback_tokens[token]['used'] = True

    student_name_for_teacher = "Anonymous"
    student_name_for_admin = session.get(
        'name', '') or ''

    if not student_name_for_admin:
        from models import Student
        student = Student.query.get(
            session.get('student_id'))
        if student:
            student_name_for_admin = student.name

    name = student_name_for_teacher
    reg = "Anonymous"
    section = "Anonymous"
    feedback = (data.get('feedback', '') or '').strip()

    if not feedback:
        return jsonify({'success': False, 'message': 'Feedback is required'}), 400

    # SENTIMENT ANALYSIS
    blob = TextBlob(feedback)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.1:
        sentiment = "✅ UNDERSTOOD"
        feedback_data["understood"] += 1
        sentiment_emoji = "😊"
    elif polarity < -0.1:
        sentiment = "❌ NOT UNDERSTOOD"
        feedback_data["not_understood"] += 1
        sentiment_emoji = "😞"
    else:
        sentiment = "⚪ NEUTRAL"
        feedback_data["neutral"] += 1
        sentiment_emoji = "😐"

    # AI SUGGESTIONS
    suggestions = generate_ai_suggestions(feedback, sentiment)

    # SAVE FEEDBACK
    feedback_entry = {
        "id": len(feedback_data["feedback_list"]) + 1,
        "name": name,
        "reg": reg,
        "section": section,
        "text": feedback,
        "sentiment": sentiment,
        "polarity": round(polarity, 2),
        "subjectivity": round(subjectivity, 2),
        "suggestions": suggestions,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    feedback_data["feedback_list"].append(feedback_entry)

    try:
        from models import Feedback as FeedbackModel
        from database import db as fdb
        token_info = feedback_tokens.get(token, {})

        teacher_id_val = token_info.get('teacher_id')

        if not teacher_id_val:
            from models import Timetable as _TT2
            _tid2 = token_info.get('timetable_id')
            if _tid2:
                _tt2 = _TT2.query.filter_by(id=int(_tid2)).first()
                if _tt2:
                    teacher_id_val = _tt2.teacher_id

        if not teacher_id_val:
            from models import Timetable as _TT3
            _tt3 = _TT3.query.first()
            if _tt3:
                teacher_id_val = _tt3.teacher_id

        print(f"Saving feedback: teacher_id={teacher_id_val}")

        new_fb = FeedbackModel(
            student_id=token_info.get('student_id'),
            teacher_id=teacher_id_val,
            student_name=student_name_for_teacher,
            registration_number='Anonymous',
            section='Anonymous',
            feedback_text=feedback,
            rating_overall=int(data.get('rating_overall') or data.get('rating') or 3),
            sentiment=sentiment,
            polarity=round(polarity, 2),
            subjectivity=round(subjectivity, 2),
            created_at=datetime.now()
        )
        fdb.session.add(new_fb)
        fdb.session.commit()
        print(f"Feedback saved to DB!")
        # Get student attendance info
        student_tokens = [
            t for t in feedback_tokens.values()
            if t.get('student_id') == new_fb.student_id
        ]
        attendance_pct = len(student_tokens)
        print(f"Student attendance count: {attendance_pct} classes")
    except Exception as e:
        print(f"DB feedback save error: {e}")

    # SEND EMAIL
    try:
        subject = f"New Feedback - {sentiment}"
        suggestions_text = "\n".join([f"  • {s}" for s in suggestions])
        
        body = f"""
Dear Teacher,

You have received new student feedback:

👤 Name: {name}
📋 Registration: {reg}
📚 Section: {section}
💬 Feedback: "{feedback}"
📊 Sentiment: {sentiment} {sentiment_emoji}
📈 Polarity Score: {polarity:.2f}

🤖 AI-Generated Suggestions:
{suggestions_text}

Dashboard Stats:
✅ Understood: {feedback_data['understood']}
❌ Not Understood: {feedback_data['not_understood']}
⚪ Neutral: {feedback_data['neutral']}

👉 View Dashboard: http://127.0.0.1:5000/dashboard

Regards,
TechAware AI Feedback System
"""

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = TEACHER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, TEACHER_EMAIL, msg.as_string())
        server.quit()

        email_status = "✅ Email sent!"
    except Exception as e:
        email_status = f"⚠️ Email failed"

    return jsonify({
        "message": "✅ Feedback saved!",
        "sentiment": sentiment,
        "polarity": polarity,
        "email_status": email_status,
        "feedback_emoji": sentiment_emoji,
        "suggestions": suggestions
    })

# ========== GET FEEDBACK SUMMARY ==========
@app.route('/get_feedback_summary', methods=['GET'])
@login_required
def get_feedback_summary():
    return jsonify(feedback_data)

# ========== DELETE FEEDBACK ==========
@app.route('/delete_feedback/<int:feedback_id>', methods=['POST'])
@login_required
@role_required(['admin', 'teacher'])
def delete_feedback(feedback_id):
    global feedback_data
    fb = next((f for f in feedback_data['feedback_list'] if f['id'] == feedback_id), None)
    
    if fb:
        if "NOT UNDERSTOOD" in fb["sentiment"]:
            feedback_data["not_understood"] -= 1
        elif "UNDERSTOOD" in fb["sentiment"]:
            feedback_data["understood"] -= 1
        else:
            feedback_data["neutral"] -= 1
        
        feedback_data["feedback_list"] = [f for f in feedback_data['feedback_list'] if f['id'] != feedback_id]
        return jsonify({"success": True, "message": "✅ Deleted!"})
    
    return jsonify({"success": False, "message": "❌ Not found!"})

# ========== EXPORT PDF ==========
@app.route('/export_pdf', methods=['GET'])
@login_required
def export_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#28a745'),
        spaceAfter=30,
        alignment=1
    )
    
    title = Paragraph("📊 TechAware Feedback Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    stats_text = f"""
    <b>Total Feedback:</b> {len(feedback_data['feedback_list'])}<br/>
    <b>Understood:</b> {feedback_data['understood']}<br/>
    <b>Not Understood:</b> {feedback_data['not_understood']}<br/>
    <b>Neutral:</b> {feedback_data['neutral']}<br/>
    """
    elements.append(Paragraph(stats_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    table_data = [["Name", "Reg", "Section", "Sentiment", "Polarity"]]
    for fb in feedback_data['feedback_list'][-10:]:
        table_data.append([
            fb["name"][:15],
            fb["reg"][:10],
            fb["section"],
            fb["sentiment"][:12],
            str(fb["polarity"])
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='feedback_report.pdf')

# ========== CLEAR ALL FEEDBACK ==========
@app.route('/clear_feedback', methods=['POST'])
@login_required
@role_required(['admin'])  # Only admin can clear all feedback
def clear_feedback():
    global feedback_data
    feedback_data = {
        "understood": 0,
        "not_understood": 0,
        "neutral": 0,
        "feedback_list": []
    }
    return jsonify({"message": "✅ All cleared!"})

# ========== ADMIN MANAGEMENT ROUTES ==========

# Admin Statistics
@app.route('/api/admin/stats', methods=['GET'])
@login_required
@role_required(['admin'])
def admin_stats():
    from models import User, Teacher, Student, Feedback, Course, Department, Batch, Section, db
    
    # Calculate statistics from database
    total_users = User.query.count()
    total_teachers = Teacher.query.count()
    total_students = Student.query.count()
    total_feedback = Feedback.query.count()
    total_courses = Course.query.count()
    total_departments = Department.query.count()
    total_batches = Batch.query.count()
    total_sections = Section.query.count()
    
    # Count pending feedback (if status field exists)
    pending_feedback = Feedback.query.filter_by().count()  # Adjust based on status field
    
    return jsonify({
        "users": total_users,
        "teachers": total_teachers,
        "students": total_students,
        "feedback": total_feedback,
        "courses": total_courses,
        "departments": total_departments,
        "batches": total_batches,
        "sections": total_sections,
        "pending": pending_feedback
    })

# User Management
@app.route('/api/admin/users', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_users():
    from models import User, db
    from werkzeug.security import generate_password_hash
    
    if request.method == 'GET':
        # Fetch all users from database
        users_query = User.query.all()
        users_list = [user.to_dict() for user in users_query]
        
        # Also include hardcoded users for backward compatibility
        for idx, (uname, info) in enumerate(users.items(), len(users_list) + 1):
            users_list.append({
                "id": idx,
                "username": uname,
                "name": info.get("name", ""),
                "email": info.get("email", ""),
                "role": info.get("role", "teacher"),
                "is_active": True
            })
        
        return jsonify({"users": users_list})
    
    elif request.method == 'POST':
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        role = data.get('role', 'teacher')
        
        if not username or not password or not name:
            return jsonify({"success": False, "message": "Username, password, and name are required!"})
        
        # Check database first
        if User.query.filter_by(username=username).first():
            return jsonify({"success": False, "message": "❌ Username already exists!"})
        
        # Check hardcoded users
        if username in users:
            return jsonify({"success": False, "message": "❌ Username already exists!"})
        
        try:
            new_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                role=role,
                name=name,
                email=email if email else None,
                is_active=True
            )
            db.session.add(new_user)
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "✅ User created successfully!",
                "user": new_user.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"❌ Error creating user: {str(e)}"})

@app.route('/api/admin/users/<int:user_id>', methods=['PUT', 'DELETE'])
@login_required
@role_required(['admin'])
def manage_user(user_id):
    from models import User, db
    from werkzeug.security import generate_password_hash

    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "❌ User not found!"})

    if request.method == 'PUT':
        data = request.json
        if data.get('password'):
            user.password_hash = generate_password_hash(data.get('password'))
        if data.get('name'):
            user.name = data.get('name')
        if data.get('email'):
            user.email = data.get('email')
        if data.get('role'):
            user.role = data.get('role')
        if 'is_active' in data:
            user.is_active = data.get('is_active')

        try:
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "✅ User updated successfully!",
                "user": user.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"❌ Error updating user: {str(e)}"})
    elif request.method == 'DELETE':
        from models import User, db
        try:
            # Try multiple ways to find user
            user = User.query.get(user_id)
            
            if not user:
                user = User.query.filter_by(
                    id=user_id).first()
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': f'User ID {user_id} not found in database!'
                })
            
            if user.email == session.get('email'):
                return jsonify({
                    'success': False,
                    'message': 'Cannot delete yourself!'
                })
            
            admin_count = User.query.filter_by(
                role='admin').count()
            if user.role == 'admin' and \
               admin_count <= 1:
                return jsonify({
                    'success': False,
                    'message': 'Cannot delete last admin!'
                })
            
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'{user.name} deleted!'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            })

@app.route('/api/admin/debug/users')
@login_required
def debug_users():
    from models import User
    users = User.query.all()
    return jsonify({
        'total': len(users),
        'users': [
            {'id': u.id, 'name': u.name, 
             'email': u.email, 'role': u.role}
            for u in users
        ]
    })

@app.route('/api/admin/debug/timetables')
@login_required
def debug_timetables():
    from models import Timetable, Teacher
    timetables = Timetable.query.all()
    result = []
    for tt in timetables:
        teacher = Teacher.query.get(tt.teacher_id)
        result.append({
            'timetable_id': tt.id,
            'teacher_id': tt.teacher_id,
            'teacher_name': teacher.name if teacher else 'NOT FOUND',
            'teacher_email': teacher.email if teacher else 'N/A',
            'course': tt.course.name if tt.course else 'N/A',
            'day': tt.day_of_week,
        })
    return jsonify({
        'total': len(timetables),
        'timetables': result
    })

# Secure User Creation Route (Admin only - No manual password)
@app.route('/api/admin/users/create', methods=['POST'])
@login_required
@role_required(['admin'])
def create_user():
    """Original route - kept for backward compatibility"""
    return create_user_secure()

@app.route('/admin/add-user', methods=['POST'])
@login_required
@role_required(['admin'])
def add_user():
    """
    Admin user creation endpoint.
    Admin provides only: Name, Email, Role
    System generates password, hashes it, saves to DB, tries to send email.
    ALWAYS returns plain text password in response for admin to copy.
    """
    return create_user_secure()

def create_user_secure():
    """
    Secure user creation endpoint for Admin.
    Admin provides only: Name, Email, Role
    System automatically generates secure password and sends via email.
    """
    from models import User, db
    
    try:
        data = request.json
        
        # Validate input
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        role = data.get('role', '').strip().lower()
        
        # Input validation
        if not name:
            return jsonify({"success": False, "message": "❌ Name is required!"}), 400
        
        if not email:
            return jsonify({"success": False, "message": "❌ Email is required!"}), 400
        
        # Validate email format (basic)
        if '@' not in email or '.' not in email.split('@')[1]:
            return jsonify({"success": False, "message": "❌ Invalid email format!"}), 400
        
        # Validate role
        valid_roles = ['admin', 'batch advisor']
        if role not in valid_roles:
            return jsonify({
                "success": False, 
                "message": f"❌ Invalid role! Must be one of: {', '.join(valid_roles)}"
            }), 400
        
        # Check if email already exists in database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                "success": False, 
                "message": "❌ Email already exists in the system!"
            }), 409
        
        # Check if username (email) already exists
        existing_username = User.query.filter_by(username=email).first()
        if existing_username:
            return jsonify({
                "success": False, 
                "message": "❌ Email already exists as username!"
            }), 409
        
        # Generate secure 8-character password with letters, digits, and special characters
        alphabet = string.ascii_letters + string.digits + string.punctuation  # a-z, A-Z, 0-9, special chars
        generated_password = ''.join(secrets.choice(alphabet) for _ in range(8))
        
        # Hash password using bcrypt
        password_bytes = generated_password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt)
        
        # Create new user
        # Use email as username since username field is required in the model
        new_user = User(
            username=email,  # Using email as username
            password_hash=password_hash.decode('utf-8'),  # Store as string
            role=role,
            name=name,
            email=email,
            is_active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Send email with credentials
        try:
            email_sent = send_user_credentials_email(name, email, generated_password, role)
            if not email_sent:
                # User created but email failed - still return success but with warning
                return jsonify({
                    "success": True,
                    "message": "✅ User created successfully, but email notification failed. Please contact the user manually.",
                    "user": new_user.to_dict(),
                    "temporary_password": generated_password,  # Return password in case email fails
                    "email_sent": False
                }), 201
        except Exception as email_error:
            # User created but email failed
            return jsonify({
                "success": True,
                "message": "✅ User created successfully, but email notification failed. Please contact the user manually.",
                "user": new_user.to_dict(),
                "temporary_password": generated_password,  # Return password in case email fails
                "email_sent": False,
                "email_error": str(email_error)
            }), 201
        
        # Success - user created and email sent
        # ALWAYS return plain text password for admin to copy manually if needed
        return jsonify({
            "success": True,
            "message": "✅ User created successfully! Login credentials have been sent to the user's email.",
            "user": new_user.to_dict(),
            "temporary_password": generated_password,  # Always return password
            "email_sent": True
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"❌ Error creating user: {str(e)}"
        }), 500


def send_user_credentials_email(name, email, password, role):
    """
    Helper function to send user credentials via email.
    Returns True if email sent successfully, False otherwise.
    """
    global smtp_config, SENDER_EMAIL, SENDER_PASSWORD
    
    try:
        subject = "Welcome to TechAware - Your Login Credentials"
        
        body = f"""Hello {name}, your account has been created. Your temporary password is: {password}. Please login and change it."""
        
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        # Use SMTP configuration (fallback to direct config if smtp_config not available)
        try:
            smtp_server = smtp_config['server']
            smtp_port = smtp_config['port']
            smtp_use_tls = smtp_config['use_tls']
            smtp_email = smtp_config['email']
            smtp_password = smtp_config['password']
        except (KeyError, NameError):
            # Fallback to direct configuration
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            smtp_use_tls = True
            smtp_email = SENDER_EMAIL
            smtp_password = SENDER_PASSWORD
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        if smtp_use_tls:
            server.starttls()
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, email, msg.as_string())
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

# Legacy endpoint for username-based deletion
@app.route('/api/admin/users/<username>', methods=['DELETE'])
@login_required
@role_required(['admin'])
def delete_user_legacy(username):
    from models import User, db
    
    # Try database first
    user = User.query.filter_by(username=username).first()
    if user:
        if user.id == session.get('user_id') or \
           user.email == session.get('email'):
            return jsonify({"success": False, "message": "❌ Cannot delete your own account!"})
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"success": True, "message": "✅ User deleted successfully!"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"❌ Error deleting user: {str(e)}"})
    
    # Fallback to hardcoded users
    if username not in users:
        return jsonify({"success": False, "message": "❌ User not found!"})
    
    if username == session.get('user_id'):
        return jsonify({"success": False, "message": "❌ Cannot delete your own account!"})
    
    del users[username]
    return jsonify({"success": True, "message": "✅ User deleted successfully!"})

# Student Management
@app.route('/api/admin/students', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_students():
    from models import Student, Department, Batch, Section, db
    from werkzeug.security import generate_password_hash
    
    if request.method == 'GET':
        # Get filter parameters
        department_id = request.args.get('department_id', type=int)
        batch_id = request.args.get('batch_id', type=int)
        section_id = request.args.get('section_id', type=int)
        search = request.args.get('search', '').strip()
        
        # Build query
        query = Student.query
        
        if department_id:
            query = query.filter_by(department_id=department_id)
        if batch_id:
            query = query.filter_by(batch_id=batch_id)
        if section_id:
            query = query.filter_by(section_id=section_id)
        if search:
            query = query.filter(
                db.or_(
                    Student.name.contains(search),
                    Student.registration_number.contains(search),
                    Student.email.contains(search)
                )
            )
        
        students = query.all()
        return jsonify({"students": [s.to_dict() for s in students]})
    
    elif request.method == 'POST':
        data = request.json
        registration_number = data.get('registration_number', '').strip().upper()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        department_id = data.get('department_id')
        batch_id = data.get('batch_id')
        section_id = data.get('section_id')
        section = data.get('section', '').strip()
        phone = data.get('phone', '').strip()
        
        if not registration_number or not name:
            return jsonify({"success": False, "message": "Registration number and name are required!"})

        if not password:
            password = secrets.token_urlsafe(8)
        
        # Check if registration number already exists
        if Student.query.filter_by(registration_number=registration_number).first():
            return jsonify({"success": False, "message": f"❌ Student with registration number '{registration_number}' already exists!"})
        
        try:
            new_student = Student(
                registration_number=registration_number,
                name=name,
                email=email if email else None,
                password_hash=generate_password_hash(password),
                department_id=department_id if department_id else None,
                batch_id=batch_id if batch_id else None,
                section_id=section_id if section_id else None,
                section=section if section else 'A',
                phone=phone if phone else None,
                is_active=True
            )
            db.session.add(new_student)
            db.session.commit()

            if email:
                try:
                    import smtplib
                    from email.mime.text import MIMEText
                    from email.mime.multipart import MIMEMultipart

                    msg = MIMEMultipart()
                    msg['From'] = SENDER_EMAIL
                    msg['To'] = email
                    msg['Subject'] = 'TechAware Student Credentials'
                    body = f"""
Dear {name},

Your student account has been created.

Roll Number: {registration_number}
Password: {password}

TechAware System
                    """
                    msg.attach(MIMEText(body, 'plain'))

                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(SENDER_EMAIL, SENDER_PASSWORD)
                    server.send_message(msg)
                    server.quit()
                except (smtplib.SMTPException, OSError) as e:
                    print(f"Student email error: {e}")

            # Enroll student in courses if provided
            course_ids = data.get('course_ids', [])
            if course_ids:
                from models import StudentCourse
                for course_id in course_ids:
                    try:
                        if course_id:
                            enrollment = StudentCourse(
                                student_id=new_student.id,
                                course_id=course_id
                            )
                            db.session.add(enrollment)
                    except Exception:
                        continue
                db.session.commit()

            return jsonify({
                "success": True,
                "message": "✅ Student created successfully!",
                "student": new_student.to_dict(),
                "auto_password": password
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"❌ Error creating student: {str(e)}"})

@app.route('/api/admin/students/<int:student_id>', methods=['PUT', 'DELETE'])
@login_required
@role_required(['admin'])
def manage_student(student_id):
    from models import Student, db
    from werkzeug.security import generate_password_hash
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"success": False, "message": "❌ Student not found!"})
    
    if request.method == 'PUT':
        data = request.json
        if data.get('name'):
            student.name = data.get('name')
        if data.get('email'):
            student.email = data.get('email')
        if data.get('password'):
            student.password_hash = generate_password_hash(data.get('password'))
        if 'department_id' in data:
            student.department_id = data.get('department_id')
        if 'batch_id' in data:
            student.batch_id = data.get('batch_id')
        if 'section_id' in data:
            student.section_id = data.get('section_id')
        if data.get('section'):
            student.section = data.get('section')
        if data.get('phone'):
            student.phone = data.get('phone')
        if 'is_active' in data:
            student.is_active = data.get('is_active')
        
        try:
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "✅ Student updated successfully!",
                "student": student.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"❌ Error updating student: {str(e)}"})
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(student)
            db.session.commit()
            return jsonify({"success": True, "message": "✅ Student deleted successfully!"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"❌ Error deleting student: {str(e)}"})

# Course Management
@app.route('/api/admin/courses', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_courses():
    from models import Course, Department, db
    
    if request.method == 'GET':
        # Fetch all courses from database
        courses_query = Course.query.all()
        courses = []
        for course in courses_query:
            course_dict = course.to_dict()
            # Add department name for display
            course_dict['department'] = course.department.name if course.department else 'N/A'
            # Ensure credit_hours is included
            course_dict['credit_hours'] = course.credit_hours if course.credit_hours else 3
            course_dict['is_active'] = course.is_active
            courses.append(course_dict)
        return jsonify({"courses": courses})
    
    elif request.method == 'POST':
        data = request.json
        code = data.get('code', '').strip().upper()
        name = data.get('name', '').strip()
        department_name = data.get('department', '').strip()
        credit_hours = data.get('credit_hours', 3)
        description = data.get('description', '').strip()
        
        if not code or not name:
            return jsonify({"success": False, "message": "Course code and name are required!"})
        
        # Check if course code already exists
        existing_course = Course.query.filter_by(code=code).first()
        if existing_course:
            return jsonify({"success": False, "message": f"❌ Course with code '{code}' already exists!"})
        
        # Find department by name or code if provided
        department_id = None
        if department_name:
            # Try to find by code first
            dept = Department.query.filter_by(code=department_name.upper()).first()
            if not dept:
                # Try to find by name
                dept = Department.query.filter_by(name=department_name).first()
            if dept:
                department_id = dept.id
            else:
                return jsonify({"success": False, "message": f"❌ Department '{department_name}' not found!"})
        
        # Create new course
        try:
            new_course = Course(
                code=code,
                name=name,
                department_id=department_id,
                credit_hours=int(credit_hours) if credit_hours else 3,
                description=description if description else None,
                is_active=True
            )
            db.session.add(new_course)
            db.session.commit()
            return jsonify({
                "success": True, 
                "message": "✅ Course created successfully!",
                "course": new_course.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"❌ Error creating course: {str(e)}"})

@app.route('/api/admin/courses/<int:course_id>', methods=['DELETE'])
@login_required
@role_required(['admin'])
def delete_course(course_id):
    from models import Course, BatchSubject, StudentCourse, Feedback, db
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"success": False, "message": "❌ Course not found!"})
    
    try:
        # Check and count related records
        batch_subjects_count = BatchSubject.query.filter_by(course_id=course_id).count()
        student_courses_count = StudentCourse.query.filter_by(course_id=course_id).count()
        feedbacks_count = Feedback.query.filter_by(course_id=course_id).count()
        
        related_records = []
        if batch_subjects_count > 0:
            related_records.append(f"{batch_subjects_count} batch assignment(s)")
        if student_courses_count > 0:
            related_records.append(f"{student_courses_count} student registration(s)")
        if feedbacks_count > 0:
            related_records.append(f"{feedbacks_count} feedback(s)")
        
        # Delete related records first (cascading delete)
        if batch_subjects_count > 0:
            # Delete CourseTeacher records associated with BatchSubjects first
            from models import CourseTeacher
            batch_subject_ids = [bs.id for bs in BatchSubject.query.filter_by(course_id=course_id).all()]
            CourseTeacher.query.filter(CourseTeacher.batch_subject_id.in_(batch_subject_ids)).delete(synchronize_session=False)
            # Delete BatchSubjects
            BatchSubject.query.filter_by(course_id=course_id).delete()
        
        # Delete StudentCourse registrations
        if student_courses_count > 0:
            StudentCourse.query.filter_by(course_id=course_id).delete()
        
        # Delete Feedbacks (keep feedbacks for historical record, or delete them)
        # Option 1: Delete feedbacks (uncomment to enable)
        # if feedbacks_count > 0:
        #     Feedback.query.filter_by(course_id=course_id).delete()
        
        # Option 2: Set course_id to NULL (keeps feedback history)
        if feedbacks_count > 0:
            Feedback.query.filter_by(course_id=course_id).update({Feedback.course_id: None}, synchronize_session=False)
        
        # Now delete the course
        db.session.delete(course)
        db.session.commit()
        
        message = "✅ Course deleted successfully!"
        if related_records:
            message += f" (Removed: {', '.join(related_records)})"
        
        return jsonify({"success": True, "message": message})
    except Exception as e:
        db.session.rollback()
        import traceback
        error_detail = str(e)
        print(f"Error deleting course: {error_detail}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": f"❌ Error deleting course: {error_detail}"})

# Teacher Management
@app.route('/api/admin/teachers', methods=['GET', 'POST'])
@login_required
def manage_teachers():
    # Manual role check instead of decorator
    if session.get('role') != 'admin':
        return jsonify({
            'success': False,
            'message': 'Admin access required'
        }), 403
    
    if request.method == 'GET':
        try:
            from models import Teacher, Department
            teachers = Teacher.query.all()
            result = []
            for t in teachers:
                dept = Department.query.filter_by(
                    name=t.department).first() if getattr(t, 'department', None) else None
                result.append({
                    'id': t.id,
                    'name': t.name,
                    'email': t.email,
                    'employee_id': getattr(
                        t, 'employee_id', 'N/A'),
                    'department': t.department or 'N/A',
                    'department_id': dept.id if dept else None,
                    'designation': getattr(
                        t, 'designation', 'N/A'),
                    'is_active': t.is_active
                })
            return jsonify({
                'success': True,
                'teachers': result,
                'total': len(result)
            })
        except Exception as e:
            import traceback
            print(f"Teachers error: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'message': str(e),
                'teachers': []
            })
    
    elif request.method == 'POST':
        from models import Teacher, Department, db
        from werkzeug.security import generate_password_hash
        import random, string

        data = request.get_json() or {}
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        department_id = data.get('department_id')
        designation = data.get('designation', '')

        if not name or not email:
            return jsonify({
                'success': False,
                'message': 'Name and email required!'
            })

        if Teacher.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'message': 'Teacher email already exists!'
            })

        department_name = None
        if department_id:
            department_id = int(department_id)
            dept = Department.query.get(department_id)
            if not dept:
                return jsonify({
                    'success': False,
                    'message': 'Department not found!'
                })
            department_name = dept.name

        auto_emp_id = f"EMP{Teacher.query.count()+1:03d}"
        auto_password = 'TCH@' + ''.join(
            random.choices(string.digits, k=4))

        new_teacher = Teacher(
            name=name,
            email=email,
            employee_id=auto_emp_id,
            department=department_name,
            designation=designation,
            password_hash=generate_password_hash(
                auto_password),
            is_active=True
        )
        db.session.add(new_teacher)
        db.session.commit()

        # Send email
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = email
            msg['Subject'] = "TechAware - Your Login Credentials"
            body = f"""
Dear {name},

Your TechAware account is ready!

Employee ID : {auto_emp_id}
Email       : {email}
Password    : {auto_password}
Role        : Teacher
Portal      : http://127.0.0.1:5000/login

TechAware System
            """
            msg.attach(MIMEText(body, 'plain'))
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            email_sent = True
        except Exception as e:
            print(f"Email error: {e}")
            email_sent = False

        return jsonify({
            'success': True,
            'message': f'Teacher added! Password: {auto_password}',
            'auto_password': auto_password,
            'employee_id': auto_emp_id,
            'email_sent': email_sent
        })

@app.route('/api/admin/teachers/<int:teacher_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@role_required(['admin'])
def manage_teacher(teacher_id):
    from models import Teacher, Department, db

    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({
            'success': False,
            'message': 'Teacher not found!'
        })

    if request.method == 'GET':
        dept = Department.query.filter_by(
            name=teacher.department).first() if getattr(teacher, 'department', None) else None
        return jsonify({
            'success': True,
            'teacher': {
                'id': teacher.id,
                'name': teacher.name,
                'email': teacher.email,
                'employee_id': getattr(
                    teacher, 'employee_id', 'N/A'),
                'department': teacher.department or 'N/A',
                'department_id': dept.id if dept else None,
                'designation': getattr(
                    teacher, 'designation', 'N/A'),
            }
        })

    elif request.method == 'PUT':
        data = request.get_json() or {}
        teacher.name = data.get('name', teacher.name)
        teacher.email = data.get('email', teacher.email)
        teacher.designation = data.get(
            'designation', teacher.designation)

        department_id = data.get('department_id')
        if department_id:
            dept = Department.query.get(int(department_id))
            if not dept:
                return jsonify({
                    'success': False,
                    'message': 'Department not found!'
                })
            teacher.department = dept.name
        elif data.get('department'):
            department_value = data.get('department')
            dept = Department.query.filter_by(
                name=department_value).first()
            if not dept:
                dept = Department.query.filter_by(
                    code=department_value.upper()).first()
            if dept:
                teacher.department = dept.name

        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Teacher updated!'
        })

    elif request.method == 'DELETE':
        from models import CourseTeacher, Timetable
        CourseTeacher.query.filter_by(
            teacher_id=teacher_id).delete()
        Timetable.query.filter_by(
            teacher_id=teacher_id).delete()
        db.session.delete(teacher)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Teacher deleted!'
        })

# Course-Teacher Assignment
@app.route('/api/admin/course-teachers', methods=['POST'])
@login_required
@role_required(['admin'])
def assign_course_teacher():
    from models import Student, db
    data = request.get_json()
    registration_number = data.get('registration_number')
    name = data.get('name')
    email = data.get('email')
    department_id = data.get('department_id')
    batch_id = data.get('batch_id')
    section_id = data.get('section_id')
    section = data.get('section')
    phone = data.get('phone')

    # Basic validation
    if not registration_number or not name:
        return jsonify({'success': False, 'message': 'Registration and name required'})

    new_student = Student(
        registration_number=registration_number,
        name=name,
        email=email,
        department_id=department_id,
        batch_id=batch_id,
        section_id=section_id,
        section=section,
        phone=phone
    )
    db.session.add(new_student)
    db.session.commit()

    # Enroll in courses if provided
    course_ids = data.get('course_ids', [])
    if course_ids:
        from models import StudentCourse
        for course_id in course_ids:
            if course_id:
                enrollment = StudentCourse(
                    student_id=new_student.id,
                    course_id=course_id
                )
                db.session.add(enrollment)
        db.session.commit()

    return jsonify({'success': True, 'student_id': new_student.id})


@app.route('/api/admin/student-courses/<int:student_id>', methods=['GET'])
@login_required
@role_required(['admin'])
def get_student_courses(student_id):
    from models import StudentCourse, Course
    enrollments = StudentCourse.query.filter_by(student_id=student_id).all()
    result = []
    for e in enrollments:
        course = Course.query.get(e.course_id)
        result.append({
            'id': e.id,
            'course_name': course.name if course else 'N/A',
            'course_id': e.course_id,
            'semester': e.semester if hasattr(e, 'semester') else ''
        })
    return jsonify({'success': True, 'enrollments': result})


@app.route('/api/admin/student-courses', methods=['POST'])
@login_required
@role_required(['admin'])
def add_student_course():
    from models import StudentCourse, db
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')

    if not student_id or not course_id:
        return jsonify({'success': False, 'message': 'student_id and course_id required'})

    existing = StudentCourse.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Already enrolled!'})

    enrollment = StudentCourse(student_id=student_id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Course added!'})


@app.route('/api/admin/student-courses/<int:enrollment_id>', methods=['DELETE'])
@login_required
@role_required(['admin'])
def remove_student_course(enrollment_id):
    from models import StudentCourse, db
    enrollment = StudentCourse.query.get(enrollment_id)
    if not enrollment:
        return jsonify({'success': False, 'message': 'Not found!'})
    db.session.delete(enrollment)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Course removed!'})
    # Find feedback and mark as approved
    fb = next((f for f in feedback_data['feedback_list'] if f['id'] == feedback_id), None)
    
    if not fb:
        return jsonify({"success": False, "message": "Feedback not found!"})
    
    # In database version, update status to 'approved'
    fb['status'] = 'approved'
    
    return jsonify({"success": True, "message": "✅ Feedback approved successfully!"})

@app.route('/api/admin/feedback/<int:feedback_id>/reject', methods=['POST'])
@login_required
@role_required(['admin'])
def reject_feedback(feedback_id):
    # Find feedback and mark as rejected
    fb = next((f for f in feedback_data['feedback_list'] if f['id'] == feedback_id), None)
    
    if not fb:
        return jsonify({"success": False, "message": "Feedback not found!"})
    
    # In database version, update status to 'rejected'
    fb['status'] = 'rejected'
    
    return jsonify({"success": True, "message": "✅ Feedback rejected!"})

# SMTP Configuration
smtp_config = {
    "server": "smtp.gmail.com",
    "port": 587,
    "use_tls": True,
    "email": SENDER_EMAIL,
    "password": SENDER_PASSWORD
}

@app.route('/api/admin/smtp-config', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_smtp_config():
    global SENDER_EMAIL, SENDER_PASSWORD, smtp_config
    
    if request.method == 'GET':
        # Return config without password
        config_safe = smtp_config.copy()
        config_safe['password'] = '***hidden***'
        return jsonify({"config": config_safe})
    
    elif request.method == 'POST':
        data = request.json
        smtp_config['server'] = data.get('server', smtp_config['server'])
        smtp_config['port'] = data.get('port', smtp_config['port'])
        smtp_config['use_tls'] = data.get('use_tls', smtp_config['use_tls'])
        
        if 'email' in data:
            smtp_config['email'] = data['email']
            SENDER_EMAIL = data['email']
        
        if 'password' in data and data['password']:
            smtp_config['password'] = data['password']
            SENDER_PASSWORD = data['password']
        
        return jsonify({"success": True, "message": "✅ SMTP configuration saved!"})

@app.route('/api/admin/test-smtp', methods=['POST'])
@login_required
@role_required(['admin'])
def test_smtp():
    data = request.json
    test_email = data.get('email', '').strip()
    
    if not test_email:
        return jsonify({"success": False, "message": "Test email address is required!"})
    
    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_config['email']
        msg["To"] = test_email
        msg["Subject"] = "[TechAware] SMTP Test Email"
        msg.attach(MIMEText("This is a test email from TechAware Feedback System. If you received this, SMTP configuration is working correctly!", "plain"))
        
        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        if smtp_config['use_tls']:
            server.starttls()
        server.login(smtp_config['email'], smtp_config['password'])
        server.sendmail(smtp_config['email'], test_email, msg.as_string())
        server.quit()
        
        return jsonify({"success": True, "message": "✅ Test email sent successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"❌ Error: {str(e)}"})

# Email Settings
email_settings = {
    "notify_new_feedback": True,
    "daily_summary": False,
    "weekly_report": False,
    "notify_approved": False,
    "default_teacher_email": TEACHER_EMAIL,
    "subject_prefix": "[TechAware]",
    "reply_to": ""
}

@app.route('/api/admin/email-settings', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_email_settings():
    global email_settings, TEACHER_EMAIL
    
    if request.method == 'GET':
        return jsonify({"settings": email_settings})
    
    elif request.method == 'POST':
        data = request.json
        email_settings.update(data)
        
        if 'default_teacher_email' in data:
            TEACHER_EMAIL = data['default_teacher_email']
        
        return jsonify({"success": True, "message": "✅ Email settings saved!"})

@app.route('/api/admin/get-summary-time', methods=['GET'])
@login_required
def get_summary_time():
    from models import SystemSettings
    t = SystemSettings.get('summary_email_time', '19:00')
    return jsonify({'success': True, 'time': t})

@app.route('/api/admin/set-summary-time', methods=['POST'])
@login_required
def set_summary_time():
    from models import SystemSettings
    data = request.get_json()
    t = data.get('time', '19:00')
    SystemSettings.set('summary_email_time', t)
    return jsonify({'success': True, 'message': f'Summary email time set to {t}'})

# Database Management
@app.route('/api/admin/database/stats', methods=['GET'])
@login_required
@role_required(['admin'])
def database_stats():
    # Calculate database statistics
    models = [
        {"name": "User", "table": "users", "count": len(users), 
         "description": "System users (admins and teachers)"},
        {"name": "Course", "table": "courses", "count": 0, 
         "description": "Course/Subject information"},
        {"name": "Teacher", "table": "teachers", "count": 0, 
         "description": "Teacher/Instructor information"},
        {"name": "Feedback", "table": "feedbacks", "count": len(feedback_data.get('feedback_list', [])), 
         "description": "Student feedback submissions"}
    ]
    
    return jsonify({
        "stats": {
            "database_type": "In-Memory / SQLite",
            "total_tables": len(models),
            "database_size": "N/A",
            "last_backup": "Never"
        },
        "models": models
    })

@app.route('/api/admin/database/backup', methods=['POST'])
@login_required
@role_required(['admin'])
def backup_database():
    # In database version, create backup file
    try:
        # Backup logic here
        return jsonify({"success": True, "message": "✅ Database backup created successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/api/admin/database/optimize', methods=['POST'])
@login_required
@role_required(['admin'])
def optimize_database():
    # In database version, run optimization queries
    try:
        # Optimization logic here
        return jsonify({"success": True, "message": "✅ Database optimized successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/api/admin/database/reset', methods=['POST'])
@login_required
@role_required(['admin'])
def reset_database():
    global feedback_data
    try:
        feedback_data = {
            "understood": 0,
            "not_understood": 0,
            "neutral": 0,
            "feedback_list": []
        }
        return jsonify({"success": True, "message": "✅ Database reset successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

# System Settings
system_settings = {
    "system_name": "TechAware Feedback System",
    "require_approval": False,
    "allow_anonymous": True,
    "enable_ai": True,
    "ai_threshold": 0.5
}

@app.route('/api/admin/system-settings', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_system_settings():
    global system_settings
    
    if request.method == 'GET':
        return jsonify({"settings": system_settings})
    
    elif request.method == 'POST':
        data = request.json
        system_settings.update(data)
        return jsonify({"success": True, "message": "✅ System settings saved!"})

# ========== DEPARTMENT MANAGEMENT ==========
@app.route('/api/admin/departments', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_departments():
    from models import Department, db
    if request.method == 'GET':
        departments = Department.query.all()
        return jsonify({"departments": [d.to_dict() for d in departments]})
    
    elif request.method == 'POST':
        data = request.json
        code = data.get('code', '').strip().upper()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not code or not name:
            return jsonify({"success": False, "message": "Department code and name are required!"})
        
        if Department.query.filter_by(code=code).first():
            return jsonify({"success": False, "message": "Department code already exists!"})
        
        dept = Department(code=code, name=name, description=description)
        db.session.add(dept)
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Department created successfully!", "department": dept.to_dict()})

@app.route('/api/admin/departments/<int:dept_id>', methods=['PUT', 'DELETE'])
@login_required
@role_required(['admin'])
def manage_department(dept_id):
    from models import Department, db
    dept = Department.query.get(dept_id)
    if not dept:
        return jsonify({"success": False, "message": "Department not found!"})
    
    if request.method == 'PUT':
        data = request.json
        dept.code = data.get('code', dept.code).strip().upper()
        dept.name = data.get('name', dept.name).strip()
        dept.description = data.get('description', dept.description)
        dept.is_active = data.get('is_active', dept.is_active)
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Department updated successfully!", "department": dept.to_dict()})
    
    elif request.method == 'DELETE':
        db.session.delete(dept)
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Department deleted successfully!"})

# ========== BATCH MANAGEMENT ==========
@app.route('/api/admin/batches', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_batches():
    from models import Batch, Department, db
    if request.method == 'GET':
        department_id = request.args.get('department_id', type=int)
        if department_id:
            batches = Batch.query.filter_by(department_id=department_id).all()
        else:
            batches = Batch.query.all()
        return jsonify({"batches": [b.to_dict() for b in batches]})
    
    elif request.method == 'POST':
        data = request.json
        department_id = data.get('department_id')
        name = data.get('name', '').strip()
        year = data.get('year')
        semester = data.get('semester', '').strip()
        
        if not department_id or not name or not year or not semester:
            return jsonify({"success": False, "message": "Department, name, year, and semester are required!"})
        
        if not Department.query.get(department_id):
            return jsonify({"success": False, "message": "Department not found!"})
        
        batch = Batch(department_id=department_id, name=name, year=year, semester=semester,
                     start_date=datetime.strptime(data.get('start_date'), '%Y-%m-%d').date() if data.get('start_date') else None,
                     end_date=datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else None)
        db.session.add(batch)
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Batch created successfully!", "batch": batch.to_dict()})

@app.route('/api/admin/batches/<int:batch_id>', methods=['PUT', 'DELETE'])
@login_required
@role_required(['admin'])
def manage_batch(batch_id):
    from models import Batch, db
    batch = Batch.query.get(batch_id)
    if not batch:
        return jsonify({"success": False, "message": "Batch not found!"})
    
    if request.method == 'PUT':
        data = request.json
        batch.name = data.get('name', batch.name).strip()
        batch.year = data.get('year', batch.year)
        batch.semester = data.get('semester', batch.semester).strip()
        batch.is_active = data.get('is_active', batch.is_active)
        if data.get('start_date'):
            batch.start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        if data.get('end_date'):
            batch.end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Batch updated successfully!", "batch": batch.to_dict()})
    
    elif request.method == 'DELETE':
        db.session.delete(batch)
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Batch deleted successfully!"})

# ========== SECTION MANAGEMENT ==========
@app.route('/api/admin/sections', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_sections():
    from models import Section, Batch, db
    if request.method == 'GET':
        batch_id = request.args.get('batch_id', type=int)
        department_id = request.args.get('department_id', type=int)
        
        if batch_id:
            sections = Section.query.filter_by(batch_id=batch_id).all()
        elif department_id:
            # Get all batches for this department, then their sections
            batches = Batch.query.filter_by(department_id=department_id).all()
            batch_ids = [b.id for b in batches]
            sections = Section.query.filter(Section.batch_id.in_(batch_ids)).all()
        else:
            sections = Section.query.all()
        return jsonify({"sections": [s.to_dict() for s in sections]})
    
    elif request.method == 'POST':
        data = request.json
        batch_id = data.get('batch_id')
        name = data.get('name', '').strip().upper()
        capacity = data.get('capacity', 50)
        
        if not batch_id or not name:
            return jsonify({"success": False, "message": "Batch and section name are required!"})
        
        if not Batch.query.get(batch_id):
            return jsonify({"success": False, "message": "Batch not found!"})
        
        if Section.query.filter_by(batch_id=batch_id, name=name).first():
            return jsonify({"success": False, "message": "Section already exists in this batch!"})
        
        section = Section(batch_id=batch_id, name=name, capacity=capacity)
        db.session.add(section)
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Section created successfully!", "section": section.to_dict()})

@app.route('/api/admin/sections/<int:section_id>', methods=['PUT', 'DELETE'])
@login_required
@role_required(['admin'])
def manage_section(section_id):
    from models import Section, db
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"success": False, "message": "Section not found!"})
    
    if request.method == 'PUT':
        data = request.json
        section.name = data.get('name', section.name).strip().upper()
        section.capacity = data.get('capacity', section.capacity)
        section.is_active = data.get('is_active', section.is_active)
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Section updated successfully!", "section": section.to_dict()})
    
    elif request.method == 'DELETE':
        db.session.delete(section)
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Section deleted successfully!"})

@app.route('/api/admin/departments/<int:dept_id>/section-count', methods=['GET'])
@login_required
@role_required(['admin'])
def get_department_section_count(dept_id):
    from models import Department, Batch, Section
    dept = Department.query.get(dept_id)
    if not dept:
        return jsonify({"success": False, "message": "Department not found!"})
    
    batches = Batch.query.filter_by(department_id=dept_id).all()
    batch_ids = [b.id for b in batches]
    sections = Section.query.filter(Section.batch_id.in_(batch_ids)).all()
    
    return jsonify({
        "success": True,
        "department": dept.to_dict(),
        "total_sections": len(sections),
        "sections_by_batch": {b.name: len([s for s in sections if s.batch_id == b.id]) for b in batches}
    })

# ========== BATCH-SUBJECT ASSIGNMENT ==========
@app.route('/api/admin/batch-subjects', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_batch_subjects():
    from models import BatchSubject, Batch, Course, db
    if request.method == 'GET':
        batch_id = request.args.get('batch_id', type=int)
        if batch_id:
            batch_subjects = BatchSubject.query.filter_by(batch_id=batch_id).all()
        else:
            batch_subjects = BatchSubject.query.all()
        return jsonify({"batch_subjects": [bs.to_dict() for bs in batch_subjects]})
    
    elif request.method == 'POST':
        data = request.json
        batch_id = data.get('batch_id')
        course_id = data.get('course_id')
        is_required = data.get('is_required', True)
        
        if not batch_id or not course_id:
            return jsonify({"success": False, "message": "Batch and course are required!"})
        
        if not Batch.query.get(batch_id):
            return jsonify({"success": False, "message": "Batch not found!"})
        if not Course.query.get(course_id):
            return jsonify({"success": False, "message": "Course not found!"})
        
        if BatchSubject.query.filter_by(batch_id=batch_id, course_id=course_id).first():
            return jsonify({"success": False, "message": "Subject already assigned to this batch!"})
        
        batch_subject = BatchSubject(batch_id=batch_id, course_id=course_id, is_required=is_required)
        db.session.add(batch_subject)
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Subject assigned to batch successfully!", "batch_subject": batch_subject.to_dict()})

@app.route('/api/admin/batch-subjects/<int:bs_id>', methods=['DELETE'])
@login_required
@role_required(['admin'])
def delete_batch_subject(bs_id):
    from models import BatchSubject, db
    bs = BatchSubject.query.get(bs_id)
    if not bs:
        return jsonify({"success": False, "message": "Assignment not found!"})
    
    db.session.delete(bs)
    db.session.commit()
    return jsonify({"success": True, "message": "✅ Subject removed from batch successfully!"})

# ========== TEACHER-SUBJECT-BATCH ASSIGNMENT ==========
@app.route('/api/admin/teacher-assignments', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_teacher_assignments():
    from models import CourseTeacher, BatchSubject, Teacher, Section, db
    if request.method == 'GET':
        batch_id = request.args.get('batch_id', type=int)
        teacher_id = request.args.get('teacher_id', type=int)
        section_id = request.args.get('section_id', type=int)
        
        query = CourseTeacher.query
        if batch_id:
            batch_subjects = BatchSubject.query.filter_by(batch_id=batch_id).all()
            bs_ids = [bs.id for bs in batch_subjects]
            query = query.filter(CourseTeacher.batch_subject_id.in_(bs_ids))
        if teacher_id:
            query = query.filter_by(teacher_id=teacher_id)
        if section_id:
            query = query.filter_by(section_id=section_id)
        
        assignments = query.all()
        return jsonify({"assignments": [a.to_dict() for a in assignments]})
    
    elif request.method == 'POST':
        data = request.json
        batch_subject_id = data.get('batch_subject_id')
        teacher_id = data.get('teacher_id')
        section_id = data.get('section_id')  # Optional
        lecture_type = data.get('lecture_type', 'Theory')
        
        if not batch_subject_id or not teacher_id:
            return jsonify({"success": False, "message": "Batch-subject and teacher are required!"})
        
        if not BatchSubject.query.get(batch_subject_id):
            return jsonify({"success": False, "message": "Batch-subject assignment not found!"})
        if not Teacher.query.get(teacher_id):
            return jsonify({"success": False, "message": "Teacher not found!"})
        if section_id and not Section.query.get(section_id):
            return jsonify({"success": False, "message": "Section not found!"})
        
        assignment = CourseTeacher(batch_subject_id=batch_subject_id, teacher_id=teacher_id,
                                  section_id=section_id, lecture_type=lecture_type)
        db.session.add(assignment)
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Teacher assigned successfully!", "assignment": assignment.to_dict()})

# Timetable Management
@app.route('/api/admin/timetable', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_timetable():
    from models import Timetable, Course, Teacher, Section, Batch, db
    from datetime import datetime, time
    
    if request.method == 'GET':
        # Get filter parameters
        department_id = request.args.get('department_id', type=int)
        batch_id = request.args.get('batch_id', type=int)
        section_id = request.args.get('section_id', type=int)
        teacher_id = request.args.get('teacher_id', type=int)
        course_id = request.args.get('course_id', type=int)
        semester = request.args.get('semester', '').strip()
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        # Build query
        query = Timetable.query
        
        if department_id:
            query = query.join(Batch).filter(Batch.department_id == department_id)
        if batch_id:
            query = query.filter_by(batch_id=batch_id)
        if section_id:
            query = query.filter_by(section_id=section_id)
        if teacher_id:
            query = query.filter_by(teacher_id=teacher_id)
        if course_id:
            query = query.filter_by(course_id=course_id)
        if semester:
            query = query.filter(Timetable.semester.contains(semester))
        if is_active:
            query = query.filter_by(is_active=True)
        
        timetables = query.order_by(Timetable.day_of_week, Timetable.start_time).all()
        return jsonify({"timetables": [t.to_dict() for t in timetables]})
    
    elif request.method == 'POST':
        data = request.json
        course_id = data.get('course_id')
        teacher_id = data.get('teacher_id')
        section_id = data.get('section_id')
        batch_id = data.get('batch_id')
        day_of_week = data.get('day_of_week')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        room = data.get('room', '').strip()
        semester = data.get('semester', '').strip()
        session_type = data.get('session_type', '').strip()
        
        if not all([course_id, teacher_id, section_id, batch_id, day_of_week is not None, start_time_str, end_time_str, semester]):
            return jsonify({"success": False, "message": "All required fields must be provided!"})
        
        try:
            # Parse time strings
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            
            # Check for conflicts
            conflicts = []
            
            # Check teacher conflict (same teacher, same day, overlapping time)
            teacher_conflicts = Timetable.query.filter_by(
                teacher_id=teacher_id,
                day_of_week=day_of_week,
                is_active=True
            ).filter(
                db.or_(
                    db.and_(
                        Timetable.start_time <= start_time,
                        Timetable.end_time > start_time
                    ),
                    db.and_(
                        Timetable.start_time < end_time,
                        Timetable.end_time >= end_time
                    ),
                    db.and_(
                        Timetable.start_time >= start_time,
                        Timetable.end_time <= end_time
                    )
                )
            ).all()
            
            if teacher_conflicts:
                for conflict in teacher_conflicts:
                    conflicts.append(f"Teacher has another class: {conflict.course.code} at {conflict.start_time.strftime('%H:%M')}-{conflict.end_time.strftime('%H:%M')}")
            
            # Check section conflict (same section, same day, overlapping time)
            section_conflicts = Timetable.query.filter_by(
                section_id=section_id,
                day_of_week=day_of_week,
                is_active=True
            ).filter(
                db.or_(
                    db.and_(
                        Timetable.start_time <= start_time,
                        Timetable.end_time > start_time
                    ),
                    db.and_(
                        Timetable.start_time < end_time,
                        Timetable.end_time >= end_time
                    ),
                    db.and_(
                        Timetable.start_time >= start_time,
                        Timetable.end_time <= end_time
                    )
                )
            ).all()
            
            if section_conflicts:
                for conflict in section_conflicts:
                    conflicts.append(f"Section has another class: {conflict.course.code} at {conflict.start_time.strftime('%H:%M')}-{conflict.end_time.strftime('%H:%M')}")
            
            # Check room conflict (same room, same day, overlapping time, if room provided)
            if room:
                room_conflicts = Timetable.query.filter_by(
                    room=room,
                    day_of_week=day_of_week,
                    is_active=True
                ).filter(
                    db.or_(
                        db.and_(
                            Timetable.start_time <= start_time,
                            Timetable.end_time > start_time
                        ),
                        db.and_(
                            Timetable.start_time < end_time,
                            Timetable.end_time >= end_time
                        ),
                        db.and_(
                            Timetable.start_time >= start_time,
                            Timetable.end_time <= end_time
                        )
                    )
                ).all()
                
                if room_conflicts:
                    for conflict in room_conflicts:
                        conflicts.append(f"Room {room} is occupied by {conflict.course.code} at {conflict.start_time.strftime('%H:%M')}-{conflict.end_time.strftime('%H:%M')}")
            
            # Create timetable entry
            new_timetable = Timetable(
                course_id=int(course_id),
                teacher_id=int(teacher_id),
                section_id=int(section_id),
                batch_id=int(batch_id),
                day_of_week=int(day_of_week),
                start_time=start_time,
                end_time=end_time,
                room=room if room else None,
                semester=semester,
                session_type=session_type if session_type else None,
                is_active=True
            )
            
            db.session.add(new_timetable)
            db.session.commit()
            
            response = {
                "success": True,
                "message": "✅ Timetable entry created successfully!",
                "timetable": new_timetable.to_dict()
            }
            
            if conflicts:
                response["conflicts"] = conflicts
                response["message"] = "⚠️ Timetable entry created but conflicts were detected!"
            
            return jsonify(response)
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"❌ Error creating timetable: {str(e)}"})

@app.route('/api/admin/timetable/<int:timetable_id>', methods=['PUT', 'DELETE'])
@login_required
@role_required(['admin'])
def manage_timetable_entry(timetable_id):
    from models import Timetable, db
    from datetime import datetime
    
    timetable = Timetable.query.get(timetable_id)
    if not timetable:
        return jsonify({"success": False, "message": "❌ Timetable entry not found!"})
    
    if request.method == 'PUT':
        data = request.json
        if 'course_id' in data:
            timetable.course_id = int(data['course_id'])
        if 'teacher_id' in data:
            timetable.teacher_id = int(data['teacher_id'])
        if 'section_id' in data:
            timetable.section_id = int(data['section_id'])
        if 'batch_id' in data:
            timetable.batch_id = int(data['batch_id'])
        if 'day_of_week' in data:
            timetable.day_of_week = int(data['day_of_week'])
        if data.get('start_time'):
            timetable.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        if data.get('end_time'):
            timetable.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        if 'room' in data:
            timetable.room = data['room'] if data['room'] else None
        if 'semester' in data:
            timetable.semester = data['semester']
        if 'session_type' in data:
            timetable.session_type = data['session_type'] if data['session_type'] else None
        if 'is_active' in data:
            timetable.is_active = data['is_active']
        
        try:
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "✅ Timetable entry updated successfully!",
                "timetable": timetable.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"❌ Error updating timetable: {str(e)}"})
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(timetable)
            db.session.commit()
            return jsonify({"success": True, "message": "✅ Timetable entry deleted successfully!"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"❌ Error deleting timetable: {str(e)}"})

@app.route('/api/admin/timetable/<int:timetable_id>', methods=['GET'])
@login_required
@role_required(['admin'])
def get_timetable(timetable_id):
    from models import Timetable
    tt = Timetable.query.get_or_404(timetable_id)
    return jsonify({'success': True, 'timetable': tt.to_dict()})

@app.route('/api/admin/timetable/<int:timetable_id>/edit', methods=['POST'])
@login_required
@role_required(['admin'])
def edit_timetable(timetable_id):
    from models import Timetable, db
    from datetime import datetime
    try:
        tt = Timetable.query.get_or_404(timetable_id)
        data = request.get_json()
        
        if 'start_time' in data:
            tt.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        if 'end_time' in data:
            tt.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        if 'day_of_week' in data:
            tt.day_of_week = int(data['day_of_week'])
        if 'room' in data:
            tt.room = data['room']
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Timetable updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/admin/teacher-assignments/<int:assignment_id>', methods=['PUT', 'DELETE'])
@login_required
@role_required(['admin'])
def manage_teacher_assignment(assignment_id):
    from models import CourseTeacher, db
    assignment = CourseTeacher.query.get(assignment_id)
    if not assignment:
        return jsonify({"success": False, "message": "Assignment not found!"})
    
    if request.method == 'PUT':
        data = request.json
        assignment.section_id = data.get('section_id', assignment.section_id)
        assignment.lecture_type = data.get('lecture_type', assignment.lecture_type)
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Assignment updated successfully!", "assignment": assignment.to_dict()})
    
    elif request.method == 'DELETE':
        db.session.delete(assignment)
        db.session.commit()
        return jsonify({"success": True, "message": "✅ Assignment removed successfully!"})

# ========== REGISTER BLUEPRINTS ==========
# Register password management blueprint
from auth import auth_bp
app.register_blueprint(auth_bp)

# ========== RUN ==========
if __name__ == '__main__':
    # Initialize database
    from database import init_db
    from models import db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///techaware.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    init_db(app)
    with app.app_context():
        db.create_all()
    
    print("🚀 Server Running...")
    print("📱 http://127.0.0.1:5000/")
    print("📊 http://127.0.0.1:5000/dashboard")
    print("🔐 http://127.0.0.1:5000/admin")
    print("⚙️ http://127.0.0.1:5000/admin_manage")
    print("👨‍🎓 http://127.0.0.1:5000/student/login")
    app.run(debug=True)
