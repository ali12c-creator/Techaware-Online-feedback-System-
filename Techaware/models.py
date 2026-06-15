"""
Database Models for TechAware Feedback System
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# This will be initialized in app.py

class User(db.Model):
    """User model for authentication (Teachers, Admins)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'name': self.name,
            'email': self.email
        }

class Department(db.Model):
    """Department model"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # e.g., CS, MATH
    name = db.Column(db.String(200), nullable=False)  # e.g., Computer Science
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    batches = db.relationship('Batch', backref='department', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'batch_count': len(self.batches) if self.batches else 0
        }

class Batch(db.Model):
    """Batch model - represents a year/semester group"""
    __tablename__ = 'batches'
    
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # e.g., Fall 2024, Spring 2025
    year = db.Column(db.Integer, nullable=False)  # e.g., 2024
    semester = db.Column(db.String(20), nullable=False)  # Fall, Spring, Summer
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sections = db.relationship('Section', backref='batch', lazy=True, cascade='all, delete-orphan')
    batch_subjects = db.relationship('BatchSubject', backref='batch', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'department_id': self.department_id,
            'department': self.department.to_dict() if self.department else None,
            'name': self.name,
            'year': self.year,
            'semester': self.semester,
            'start_date': self.start_date.strftime("%Y-%m-%d") if self.start_date else None,
            'end_date': self.end_date.strftime("%Y-%m-%d") if self.end_date else None,
            'is_active': self.is_active,
            'section_count': len(self.sections) if self.sections else 0
        }

class Section(db.Model):
    """Section model - sections within a batch"""
    __tablename__ = 'sections'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    name = db.Column(db.String(10), nullable=False)  # e.g., A, B, C
    capacity = db.Column(db.Integer, default=50)
    current_students = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: one section per name per batch
    __table_args__ = (db.UniqueConstraint('batch_id', 'name', name='unique_batch_section'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'batch': self.batch.to_dict() if self.batch else None,
            'name': self.name,
            'capacity': self.capacity,
            'current_students': self.current_students,
            'is_active': self.is_active
        }

class Course(db.Model):
    """Course/Subject model"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # e.g., CS101
    name = db.Column(db.String(200), nullable=False)  # e.g., Introduction to Computer Science
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    credit_hours = db.Column(db.Integer, default=3)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', backref='courses')
    feedbacks = db.relationship('Feedback', backref='course', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'department_id': self.department_id,
            'department': self.department.to_dict() if self.department else None,
            'credit_hours': self.credit_hours,
            'description': self.description
        }

class Teacher(db.Model):
    """Teacher/Instructor model"""
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    designation = db.Column(db.String(100), nullable=True)  # Professor, Associate Professor, etc.
    password_hash = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    feedbacks = db.relationship('Feedback', backref='teacher', lazy=True)
    course_assignments = db.relationship('CourseTeacher', back_populates='teacher', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'employee_id': self.employee_id,
            'department_id': self.department_id,
            'department': self.department,
            'designation': self.designation
        }

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class BatchSubject(db.Model):
    """Many-to-Many relationship between Batches and Courses (Subjects assigned to batches)"""
    __tablename__ = 'batch_subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    is_required = db.Column(db.Boolean, default=True)  # Required or elective
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='batch_assignments', overlaps="batch_subjects")
    teacher_assignments = db.relationship('CourseTeacher', backref='batch_subject', lazy=True, cascade='all, delete-orphan')
    
    # Unique constraint: one subject per batch
    __table_args__ = (db.UniqueConstraint('batch_id', 'course_id', name='unique_batch_course'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'batch': self.batch.to_dict() if self.batch else None,
            'course_id': self.course_id,
            'course': self.course.to_dict() if self.course else None,
            'is_required': self.is_required
        }

class CourseTeacher(db.Model):
    """Teacher assignment to subjects in specific batches and sections"""
    __tablename__ = 'course_teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_subject_id = db.Column(db.Integer, db.ForeignKey('batch_subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=True)  # Specific section
    lecture_type = db.Column(db.String(20), nullable=True)  # Theory, Practical, Seminar
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('Teacher', back_populates='course_assignments')
    section = db.relationship('Section', backref='teacher_assignments')
    
    def to_dict(self):
        batch_subject = self.batch_subject
        return {
            'id': self.id,
            'batch_subject_id': self.batch_subject_id,
            'batch_subject': batch_subject.to_dict() if batch_subject else None,
            'teacher_id': self.teacher_id,
            'teacher': self.teacher.to_dict() if self.teacher else None,
            'section_id': self.section_id,
            'section': self.section.to_dict() if self.section else None,
            'lecture_type': self.lecture_type
        }

class Student(db.Model):
    """Student model with authentication"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=True)
    section = db.Column(db.String(10), nullable=False)  # Keep for backward compatibility
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', backref='students')
    batch = db.relationship('Batch', backref='students')
    section_obj = db.relationship('Section', backref='students')
    registered_courses = db.relationship('StudentCourse', backref='student', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='student_obj', lazy=True, foreign_keys='Feedback.student_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'registration_number': self.registration_number,
            'name': self.name,
            'email': self.email,
            'department_id': self.department_id,
            'department': self.department.to_dict() if self.department else None,
            'batch_id': self.batch_id,
            'batch': self.batch.to_dict() if self.batch else None,
            'section_id': self.section_id,
            'section': self.section,
            'section_obj': self.section_obj.to_dict() if self.section_obj else None,
            'phone': self.phone
        }

class StudentCourse(db.Model):
    """Many-to-Many relationship between Students and Courses (Course Registration)"""
    __tablename__ = 'student_courses'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    semester = db.Column(db.String(20), nullable=True)
    section = db.Column(db.String(10), nullable=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='student_registrations')
    
    # Unique constraint: one registration per student per course per semester
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', 'semester', name='unique_student_course_semester'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'course': self.course.to_dict() if self.course else None,
            'semester': self.semester,
            'section': self.section,
            'registered_at': self.registered_at.strftime("%Y-%m-%d %H:%M:%S") if self.registered_at else None
        }

class Timetable(db.Model):
    """Timetable model for scheduling lectures"""
    __tablename__ = 'timetables'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(50), nullable=True)
    semester = db.Column(db.String(50), nullable=False)  # e.g., "Fall 2024"
    session_type = db.Column(db.String(20), nullable=True)  # Morning/Evening
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='timetables')
    teacher = db.relationship('Teacher', backref='timetables')
    section = db.relationship('Section', backref='timetables')
    batch = db.relationship('Batch', backref='timetables')
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'course': self.course.to_dict() if self.course else None,
            'teacher_id': self.teacher_id,
            'teacher': self.teacher.to_dict() if self.teacher else None,
            'section_id': self.section_id,
            'section': self.section.to_dict() if self.section else None,
            'batch_id': self.batch_id,
            'batch': self.batch.to_dict() if self.batch else None,
            'day_of_week': self.day_of_week,
            'day_name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][self.day_of_week],
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'room': self.room,
            'semester': self.semester,
            'session_type': self.session_type,
            'is_active': self.is_active
        }

class Feedback(db.Model):
    """Student Feedback model"""
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Student Information
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)  # Link to Student model
    student_name = db.Column(db.String(100), nullable=False)
    registration_number = db.Column(db.String(50), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    
    # Course & Teacher Information
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)
    
    # Feedback Content
    feedback_text = db.Column(db.Text, nullable=False)
    lecture_type = db.Column(db.String(20), nullable=True)  # Theory, Practical, Seminar
    
    # Structured Ratings (1-5 scale)
    rating_overall = db.Column(db.Integer, nullable=True)  # 1-5 stars
    rating_clarity = db.Column(db.Integer, nullable=True)
    rating_punctuality = db.Column(db.Integer, nullable=True)
    rating_material_quality = db.Column(db.Integer, nullable=True)
    rating_communication = db.Column(db.Integer, nullable=True)
    
    # Sentiment Analysis
    sentiment = db.Column(db.String(50), nullable=False)  # UNDERSTOOD, NOT UNDERSTOOD, NEUTRAL
    polarity = db.Column(db.Float, nullable=False)
    subjectivity = db.Column(db.Float, nullable=False)
    
    # AI Suggestions
    suggestions = db.Column(db.Text, nullable=True)  # JSON string of suggestions
    
    # Positive Aspects (checkboxes)
    positive_aspects = db.Column(db.Text, nullable=True)  # JSON string
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'name': self.student_name,
            'reg': self.registration_number,
            'section': self.section,
            'course_id': self.course_id,
            'course': self.course.to_dict() if self.course else None,
            'teacher_id': self.teacher_id,
            'teacher': self.teacher.to_dict() if self.teacher else None,
            'text': self.feedback_text,
            'lecture_type': self.lecture_type,
            'rating_overall': self.rating_overall,
            'rating_clarity': self.rating_clarity,
            'rating_punctuality': self.rating_punctuality,
            'rating_material_quality': self.rating_material_quality,
            'rating_communication': self.rating_communication,
            'sentiment': self.sentiment,
            'polarity': self.polarity,
            'subjectivity': self.subjectivity,
            'suggestions': json.loads(self.suggestions) if self.suggestions else [],
            'positive_aspects': json.loads(self.positive_aspects) if self.positive_aspects else [],
            'timestamp': self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class SystemSettings(db.Model):
    """Global system settings set by admin"""
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=True)

    @staticmethod
    def get(key, default=None):
        s = SystemSettings.query.filter_by(key=key).first()
        return s.value if s else default

    @staticmethod
    def set(key, value):
        s = SystemSettings.query.filter_by(key=key).first()
        if s:
            s.value = value
        else:
            s = SystemSettings(key=key, value=value)
            db.session.add(s)
        db.session.commit()

class FeedbackToken(db.Model):
    __tablename__ = 'feedback_tokens_db'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    student_id = db.Column(db.Integer, nullable=True)
    timetable_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    used = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)

