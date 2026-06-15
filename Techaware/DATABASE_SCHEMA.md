# Complete Database Schema Design
## TechAware Feedback System - Enhanced Architecture

---

## 📊 Database Models & Relationships

### 1. **Department Model**
```python
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # e.g., "Computer Science"
    code = db.Column(db.String(20), unique=True, nullable=False)  # e.g., "CS"
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    batches = db.relationship('Batch', backref='department', lazy=True)
    students = db.relationship('Student', backref='department', lazy=True)
    teachers = db.relationship('Teacher', backref='department', lazy=True)
    courses = db.relationship('Course', backref='department', lazy=True)
```

### 2. **Batch Model**
```python
class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)  # e.g., 2024
    name = db.Column(db.String(100), nullable=False)  # e.g., "Fall 2024"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sections = db.relationship('Section', backref='batch', lazy=True)
    students = db.relationship('Student', backref='batch', lazy=True)
    timetables = db.relationship('Timetable', backref='batch', lazy=True)
```

### 3. **Section Model**
```python
class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)  # e.g., "A", "B", "C"
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    capacity = db.Column(db.Integer, default=50)
    current_strength = db.Column(db.Integer, default=0)
    room = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='section', lazy=True)
    timetables = db.relationship('Timetable', backref='section', lazy=True)
```

### 4. **Student Model** (Enhanced)
```python
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    cnic = db.Column(db.String(20), unique=True, nullable=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Active')  # Active/Suspended/Graduated
    profile_picture = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    feedbacks = db.relationship('Feedback', backref='student', lazy=True)
```

### 5. **Timetable Model**
```python
class Timetable(db.Model):
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
    session = db.Column(db.String(20), nullable=True)  # Morning/Evening
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lecture_sessions = db.relationship('LectureSession', backref='timetable', lazy=True)
```

### 6. **Lecture Session Model**
```python
class LectureSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timetable_id = db.Column(db.Integer, db.ForeignKey('timetables.id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    actual_date = db.Column(db.Date, nullable=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=True)
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled/In Progress/Completed/Cancelled
    topic = db.Column(db.String(500), nullable=True)
    attendance_taken = db.Column(db.Boolean, default=False)
    feedback_window_open = db.Column(db.Boolean, default=False)
    feedback_window_closed = db.Column(db.Boolean, default=False)
    feedback_deadline = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='lecture_session', lazy=True)
    feedbacks = db.relationship('Feedback', backref='lecture_session', lazy=True)
```

### 7. **Attendance Model**
```python
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('lecture_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # Present/Absent/Late
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)
    marked_by = db.Column(db.String(50), nullable=True)  # Teacher username or "System"
    feedback_submitted = db.Column(db.Boolean, default=False)
    feedback_submitted_at = db.Column(db.DateTime, nullable=True)
    
    # Unique constraint: one attendance record per student per session
    __table_args__ = (db.UniqueConstraint('session_id', 'student_id', name='unique_session_student'),)
```

### 8. **Feedback Model** (Enhanced)
```python
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Student Information
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    registration_number = db.Column(db.String(50), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    
    # Session & Course Information
    session_id = db.Column(db.Integer, db.ForeignKey('lecture_sessions.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    
    # Feedback Content
    feedback_text = db.Column(db.Text, nullable=False)
    lecture_type = db.Column(db.String(20), nullable=True)  # Theory/Practical/Seminar
    
    # Structured Ratings (1-5 scale)
    rating_clarity = db.Column(db.Integer, nullable=True)
    rating_punctuality = db.Column(db.Integer, nullable=True)
    rating_material_quality = db.Column(db.Integer, nullable=True)
    rating_communication = db.Column(db.Integer, nullable=True)
    rating_overall = db.Column(db.Integer, nullable=True)
    
    # Sentiment Analysis
    sentiment = db.Column(db.String(50), nullable=False)  # UNDERSTOOD/NOT UNDERSTOOD/NEUTRAL
    polarity = db.Column(db.Float, nullable=False)
    subjectivity = db.Column(db.Float, nullable=False)
    
    # AI Suggestions
    suggestions = db.Column(db.Text, nullable=True)  # JSON array
    
    # Positive Aspects
    positive_aspects = db.Column(db.Text, nullable=True)  # JSON array
    
    # Approval Workflow
    status = db.Column(db.String(20), default='submitted')  # submitted/approved/rejected
    is_anonymous = db.Column(db.Boolean, default=False)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.String(50), nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 9. **Feedback Aggregation Model**
```python
class FeedbackAggregation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('lecture_sessions.id'), unique=True, nullable=False)
    
    # Aggregation Statistics
    total_present_students = db.Column(db.Integer, nullable=False)
    total_feedbacks_submitted = db.Column(db.Integer, default=0)
    aggregation_complete = db.Column(db.Boolean, default=False)
    aggregated_at = db.Column(db.DateTime, nullable=True)
    
    # Aggregated Ratings (Averages)
    avg_clarity = db.Column(db.Float, nullable=True)
    avg_punctuality = db.Column(db.Float, nullable=True)
    avg_material_quality = db.Column(db.Float, nullable=True)
    avg_communication = db.Column(db.Float, nullable=True)
    avg_overall = db.Column(db.Float, nullable=True)
    
    # Aggregated Sentiment
    total_understood = db.Column(db.Integer, default=0)
    total_not_understood = db.Column(db.Integer, default=0)
    total_neutral = db.Column(db.Integer, default=0)
    avg_polarity = db.Column(db.Float, nullable=True)
    
    # AI Suggestions (Aggregated)
    aggregated_suggestions = db.Column(db.Text, nullable=True)  # JSON array
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

### 10. **Teacher Performance Model**
```python
class TeacherPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    period = db.Column(db.String(50), nullable=False)  # e.g., "Fall 2024", "2024"
    
    # Performance Metrics
    total_feedbacks = db.Column(db.Integer, default=0)
    total_sessions = db.Column(db.Integer, default=0)
    
    # Average Ratings
    avg_clarity = db.Column(db.Float, nullable=True)
    avg_punctuality = db.Column(db.Float, nullable=True)
    avg_material_quality = db.Column(db.Float, nullable=True)
    avg_communication = db.Column(db.Float, nullable=True)
    avg_overall = db.Column(db.Float, nullable=True)
    
    # Sentiment Distribution
    total_understood = db.Column(db.Integer, default=0)
    total_not_understood = db.Column(db.Integer, default=0)
    total_neutral = db.Column(db.Integer, default=0)
    avg_polarity = db.Column(db.Float, nullable=True)
    
    # Performance Score (0-100)
    performance_score = db.Column(db.Float, nullable=True)
    
    # Improvement Areas (JSON)
    improvement_areas = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Unique constraint: one performance record per teacher per period
    __table_args__ = (db.UniqueConstraint('teacher_id', 'period', name='unique_teacher_period'),)
```

### 11. **Notification Model**
```python
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)  # username
    user_role = db.Column(db.String(20), nullable=False)  # student/teacher/admin
    type = db.Column(db.String(50), nullable=False)  # feedback_pending, feedback_complete, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500), nullable=True)  # URL to relevant page
    read_status = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 12. **System Configuration Model**
```python
class SystemConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)  # email/smtp/system/ai
    data_type = db.Column(db.String(20), default='string')  # string/number/boolean/json
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

---

## 🔗 Key Relationships

### Student → Batch → Section → Department
- One student belongs to one batch
- One batch has many sections
- One student belongs to one section
- One batch belongs to one department
- One student belongs to one department

### Timetable → Course → Teacher → Section → Batch
- One timetable entry links course, teacher, section, and batch
- One course can be in multiple timetables
- One teacher can teach multiple courses/sections

### Lecture Session → Timetable
- One timetable generates multiple lecture sessions (one per week)
- One lecture session belongs to one timetable

### Attendance → Lecture Session → Student
- One attendance record per student per session
- One session has many attendance records
- One student has many attendance records

### Feedback → Lecture Session → Student → Course → Teacher
- One feedback per student per session
- One session can have multiple feedbacks (from different students)
- Feedback links to student, course, and teacher

### Feedback Aggregation → Lecture Session
- One aggregation per lecture session
- Aggregation created after all present students submit

---

## 📊 Database Indexes

```python
# Performance indexes
db.Index('idx_student_reg', Student.registration_number)
db.Index('idx_student_batch_section', Student.batch_id, Student.section_id)
db.Index('idx_timetable_teacher', Timetable.teacher_id)
db.Index('idx_timetable_section', Timetable.section_id)
db.Index('idx_session_date', LectureSession.scheduled_date)
db.Index('idx_attendance_session_student', Attendance.session_id, Attendance.student_id)
db.Index('idx_feedback_session', Feedback.session_id)
db.Index('idx_feedback_student', Feedback.student_id)
db.Index('idx_feedback_teacher', Feedback.teacher_id)
```

---

## 🔄 Data Flow

```
Timetable Created
    ↓
Auto-generate Lecture Sessions (weekly)
    ↓
Teacher Marks Attendance (or Automatic)
    ↓
Lecture Completes → Feedback Window Opens (for present students only)
    ↓
Students Submit Feedback
    ↓
Track Submissions (count present vs submitted)
    ↓
All Present Students Submit → Trigger Aggregation
    ↓
Run Sentiment Analysis on All Feedback
    ↓
Generate AI Suggestions
    ↓
Create Feedback Aggregation Record
    ↓
Update Teacher Performance Metrics
    ↓
Notify Teacher
    ↓
Display Results on Teacher Portal
```

---

This schema supports the complete system requirements!

