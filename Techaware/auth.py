"""
Password Management Module for TechAware Feedback System
Handles: Forgot Password, Reset Password, and Change Password
"""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from models import User, Student, db
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import bcrypt
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Default values (will be accessed from app config)
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')

# Token expiration time (1 hour)
TOKEN_EXPIRATION = 3600


def get_serializer():
    """Get serializer with app's secret key"""
    from flask import current_app
    secret_key = current_app.secret_key
    return URLSafeTimedSerializer(secret_key)

# Token expiration time (1 hour)
TOKEN_EXPIRATION = 3600


def send_password_reset_email(email, name, reset_link):
    """
    Send password reset email to user
    """
    try:
        subject = "TechAware - Password Reset Request"
        
        body = f"""Hello {name},

You have requested to reset your password for your TechAware account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

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
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, email, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return False


def verify_password_hash(password_hash, password):
    """
    Verify password against hash (supports both bcrypt and werkzeug)
    """
    # Check if it's a bcrypt hash (starts with $2a$, $2b$, or $2y$)
    if password_hash.startswith('$2'):
        try:
            password_bytes = password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False
    else:
        # Use werkzeug for old passwords
        return check_password_hash(password_hash, password)


def hash_password(password):
    """
    Hash password using bcrypt
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)
    return password_hash.decode('utf-8')


# ========== FORGOT PASSWORD ROUTES ==========

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Forgot Password - Public route
    Accepts email, generates token, sends reset link
    """
    if request.method == 'GET':
        return render_template('forgot_password.html')
    
    # POST request
    data = request.get_json() if request.is_json else request.form
    email = (data.get('email', '') or '').strip()
    
    if not email:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ Email is required!"}), 400
        flash("❌ Email is required!", "error")
        return render_template('forgot_password.html')
    
    # Check if user exists (check both User and Student tables)
    user = User.query.filter_by(email=email).first()
    student = None
    
    if not user:
        student = Student.query.filter_by(email=email).first()
    
    # Don't reveal if email exists (security best practice)
    if not user and not student:
        if request.is_json:
            return jsonify({
                "success": True,
                "message": "✅ If an account with that email exists, a password reset link has been sent."
            })
        flash("✅ If an account with that email exists, a password reset link has been sent.", "success")
        return render_template('forgot_password.html')
    
    # Generate token
    user_type = 'user' if user else 'student'
    user_id = user.id if user else student.id
    
    token_data = {
        'email': email,
        'user_type': user_type,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    try:
        serializer = get_serializer()
        token = serializer.dumps(token_data, salt='password-reset')
        
        # Generate reset link
        reset_link = request.url_root.rstrip('/') + url_for('auth.reset_password', token=token)
        
        # Send email
        name = user.name if user else student.name
        email_sent = send_password_reset_email(email, name, reset_link)
        
        if email_sent:
            if request.is_json:
                return jsonify({
                    "success": True,
                    "message": "✅ Password reset link has been sent to your email!"
                })
            flash("✅ Password reset link has been sent to your email!", "success")
        else:
            if request.is_json:
                return jsonify({
                    "success": False,
                    "message": "❌ Failed to send email. Please try again later."
                }), 500
            flash("❌ Failed to send email. Please try again later.", "error")
        
        return render_template('forgot_password.html')
        
    except Exception as e:
        print(f"Error generating reset token: {str(e)}")
        if request.is_json:
            return jsonify({
                "success": False,
                "message": "❌ An error occurred. Please try again later."
            }), 500
        flash("❌ An error occurred. Please try again later.", "error")
        return render_template('forgot_password.html')


# ========== RESET PASSWORD ROUTES ==========

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Reset Password - Public route (with token)
    Validates token and allows user to set new password
    """
    if request.method == 'GET':
        # Validate token
        try:
            serializer = get_serializer()
            token_data = serializer.loads(token, salt='password-reset', max_age=TOKEN_EXPIRATION)
            return render_template('reset_password.html', token=token, valid=True)
        except SignatureExpired:
            flash("❌ The password reset link has expired. Please request a new one.", "error")
            return render_template('reset_password.html', token=None, valid=False, error="expired")
        except BadSignature:
            flash("❌ Invalid password reset link. Please request a new one.", "error")
            return render_template('reset_password.html', token=None, valid=False, error="invalid")
        except Exception as e:
            print(f"Error validating token: {str(e)}")
            flash("❌ An error occurred. Please try again.", "error")
            return render_template('reset_password.html', token=None, valid=False, error="error")
    
    # POST request
    data = request.get_json() if request.is_json else request.form
    new_password = (data.get('new_password', '') or data.get('password', '') or '').strip()
    confirm_password = (data.get('confirm_password', '') or data.get('confirm', '') or '').strip()
    
    # Validate token
    try:
        serializer = get_serializer()
        token_data = serializer.loads(token, salt='password-reset', max_age=TOKEN_EXPIRATION)
        email = token_data.get('email')
        user_type = token_data.get('user_type')
        user_id = token_data.get('user_id')
    except SignatureExpired:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ The password reset link has expired. Please request a new one."}), 400
        flash("❌ The password reset link has expired. Please request a new one.", "error")
        return redirect(url_for('auth.forgot_password'))
    except BadSignature:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ Invalid password reset link."}), 400
        flash("❌ Invalid password reset link.", "error")
        return redirect(url_for('auth.forgot_password'))
    except Exception as e:
        print(f"Error validating token: {str(e)}")
        if request.is_json:
            return jsonify({"success": False, "message": "❌ An error occurred. Please try again."}), 500
        flash("❌ An error occurred. Please try again.", "error")
        return redirect(url_for('auth.forgot_password'))
    
    # Validate password
    if not new_password or len(new_password) < 6:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ Password must be at least 6 characters long!"}), 400
        flash("❌ Password must be at least 6 characters long!", "error")
        return render_template('reset_password.html', token=token, valid=True)
    
    if new_password != confirm_password:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ Passwords do not match!"}), 400
        flash("❌ Passwords do not match!", "error")
        return render_template('reset_password.html', token=token, valid=True)
    
    # Get user
    if user_type == 'user':
        user = User.query.get(user_id)
        if not user or user.email != email:
            if request.is_json:
                return jsonify({"success": False, "message": "❌ User not found!"}), 404
            flash("❌ User not found!", "error")
            return redirect(url_for('auth.forgot_password'))
        
        # Hash and update password
        user.password_hash = hash_password(new_password)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                "success": True,
                "message": "✅ Password reset successfully! You can now login with your new password."
            })
        flash("✅ Password reset successfully! You can now login with your new password.", "success")
        return redirect(url_for('admin_panel'))
    
    else:  # student
        student = Student.query.get(user_id)
        if not student or student.email != email:
            if request.is_json:
                return jsonify({"success": False, "message": "❌ Student not found!"}), 404
            flash("❌ Student not found!", "error")
            return redirect(url_for('auth.forgot_password'))
        
        # Hash and update password
        student.password_hash = hash_password(new_password)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                "success": True,
                "message": "✅ Password reset successfully! You can now login with your new password."
            })
        flash("✅ Password reset successfully! You can now login with your new password.", "success")
        return redirect(url_for('student_login_page'))


# ========== CHANGE PASSWORD ROUTE ==========

@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """
    Change Password - Protected route (requires login)
    Allows logged-in users to change their password
    """
    # Check if user is logged in
    if 'user_id' not in session and 'student_id' not in session:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ Please login first!"}), 401
        flash("❌ Please login first!", "error")
        return redirect(url_for('admin_panel'))
    
    if request.method == 'GET':
        return render_template('change_password.html')
    
    # POST request
    data = request.get_json() if request.is_json else request.form
    current_password = (data.get('current_password', '') or data.get('old_password', '') or '').strip()
    new_password = (data.get('new_password', '') or data.get('password', '') or '').strip()
    confirm_password = (data.get('confirm_password', '') or data.get('confirm', '') or '').strip()
    
    # Validate input
    if not current_password or not new_password or not confirm_password:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ All fields are required!"}), 400
        flash("❌ All fields are required!", "error")
        return render_template('change_password.html')
    
    if len(new_password) < 6:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ New password must be at least 6 characters long!"}), 400
        flash("❌ New password must be at least 6 characters long!", "error")
        return render_template('change_password.html')
    
    if new_password != confirm_password:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ New passwords do not match!"}), 400
        flash("❌ New passwords do not match!", "error")
        return render_template('change_password.html')
    
    if current_password == new_password:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ New password must be different from current password!"}), 400
        flash("❌ New password must be different from current password!", "error")
        return render_template('change_password.html')
    
    # Get user based on session
    user = None
    student = None
    
    if 'user_id' in session:
        # Teacher/Admin user
        user_id = session.get('user_id')
        user = User.query.filter_by(username=user_id).first()
        if not user:
            # Try by email
            user = User.query.filter_by(email=user_id).first()
    elif 'student_id' in session:
        # Student
        student_id = session.get('student_id')
        student = Student.query.get(student_id)
    
    if not user and not student:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ User not found!"}), 404
        flash("❌ User not found!", "error")
        return redirect(url_for('admin_panel'))
    
    # Verify current password
    if user:
        password_valid = verify_password_hash(user.password_hash, current_password)
    else:
        password_valid = verify_password_hash(student.password_hash, current_password)
    
    if not password_valid:
        if request.is_json:
            return jsonify({"success": False, "message": "❌ Current password is incorrect!"}), 400
        flash("❌ Current password is incorrect!", "error")
        return render_template('change_password.html')
    
    # Update password
    try:
        if user:
            user.password_hash = hash_password(new_password)
        else:
            student.password_hash = hash_password(new_password)
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                "success": True,
                "message": "✅ Password changed successfully!"
            })
        flash("✅ Password changed successfully!", "success")
        return render_template('change_password.html')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error changing password: {str(e)}")
        if request.is_json:
            return jsonify({
                "success": False,
                "message": f"❌ An error occurred: {str(e)}"
            }), 500
        flash(f"❌ An error occurred: {str(e)}", "error")
        return render_template('change_password.html')

