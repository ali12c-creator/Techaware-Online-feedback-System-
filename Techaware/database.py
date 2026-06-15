"""
Database initialization and setup
"""
from models import db, User, Course, Teacher, CourseTeacher, Student, StudentCourse, Department, Batch, Section, BatchSubject
from werkzeug.security import generate_password_hash
from datetime import date
import sqlite3
import os

def migrate_database(app):
    """Check and migrate database schema if needed.

    IMPORTANT: This is a *non-destructive* migration. Older versions of this
    function used to call db.drop_all() (which wipes EVERY table - all your
    teachers, students, attendance, etc.) whenever the schema looked out of
    date. That is why data kept disappearing and you had to re-enter
    everything after every restart.

    Instead, this version compares each model's columns against the actual
    columns in the SQLite tables, and simply ADDS any missing columns with
    ALTER TABLE ... ADD COLUMN. Existing rows and data are kept untouched.
    """
    db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
    if not db_path:
        return False
    
    # Flask-SQLAlchemy by default creates database in instance/ folder
    # Check both root and instance/ directory
    possible_paths = [
        db_path,
        os.path.join('instance', db_path),
        os.path.join(app.instance_path, db_path) if hasattr(app, 'instance_path') else None
    ]
    possible_paths = [p for p in possible_paths if p and os.path.exists(p)]
    
    if not possible_paths:
        # Database doesn't exist yet - db.create_all() will build it fresh
        return False
    
    db_path = possible_paths[0]
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        added_any = False

        # Go through every model/table defined in models.py
        for table in db.metadata.sorted_tables:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table.name,)
            )
            if not cursor.fetchone():
                # Table doesn't exist yet at all - db.create_all() will create it
                continue

            cursor.execute(f"PRAGMA table_info({table.name})")
            existing_columns = {row[1] for row in cursor.fetchall()}

            for column in table.columns:
                if column.name in existing_columns:
                    continue

                col_type = str(column.type)
                try:
                    cursor.execute(
                        f"ALTER TABLE {table.name} ADD COLUMN {column.name} {col_type}"
                    )
                    print(f"✅ Added missing column '{column.name}' to table '{table.name}'")
                    added_any = True
                except Exception as col_err:
                    print(f"⚠️  Could not add column '{column.name}' to '{table.name}': {col_err}")

        conn.commit()
        conn.close()
        return added_any
    except Exception as e:
        print(f"⚠️  Migration check failed: {e}")
        # Continue with normal initialization
        return False

def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    
    with app.app_context():
        # Add any columns that are missing from existing tables (no data loss)
        migrate_database(app)

        # Create any tables that don't exist yet (won't touch existing tables)
        db.create_all()
        
        # Initialize departments if empty
        if Department.query.count() == 0:
            departments = [
                Department(code='CS', name='Computer Science', description='Department of Computer Science'),
                Department(code='MATH', name='Mathematics', description='Department of Mathematics'),
                Department(code='ENG', name='English', description='Department of English'),
                Department(code='EE', name='Electrical Engineering', description='Department of Electrical Engineering'),
            ]
            for dept in departments:
                db.session.add(dept)
            db.session.commit()
        
        # Initialize batches if empty
        if Batch.query.count() == 0:
            cs_dept = Department.query.filter_by(code='CS').first()
            math_dept = Department.query.filter_by(code='MATH').first()
            
            if cs_dept:
                batches = [
                    Batch(department_id=cs_dept.id, name='Fall 2024', year=2024, semester='Fall', 
                         start_date=date(2024, 9, 1), end_date=date(2024, 12, 31)),
                    Batch(department_id=cs_dept.id, name='Spring 2025', year=2025, semester='Spring',
                         start_date=date(2025, 2, 1), end_date=date(2025, 6, 30)),
                ]
                for batch in batches:
                    db.session.add(batch)
            
            if math_dept:
                batches = [
                    Batch(department_id=math_dept.id, name='Fall 2024', year=2024, semester='Fall',
                         start_date=date(2024, 9, 1), end_date=date(2024, 12, 31)),
                ]
                for batch in batches:
                    db.session.add(batch)
            
            db.session.commit()
        
        # Initialize sections if empty
        if Section.query.count() == 0:
            cs_batches = Batch.query.join(Department).filter(Department.code == 'CS').all()
            for batch in cs_batches:
                sections = [
                    Section(batch_id=batch.id, name='A', capacity=50),
                    Section(batch_id=batch.id, name='B', capacity=50),
                    Section(batch_id=batch.id, name='C', capacity=50),
                ]
                for section in sections:
                    db.session.add(section)
            db.session.commit()
        
        # Initialize default data if tables are empty
        if User.query.count() == 0:
            from werkzeug.security import generate_password_hash
            
            # Only Admin
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                name='Administrator',
                email='admin@comsats.edu.pk',
                is_active=True
            )
            db.session.add(admin)
            
            # Only Batch Advisor
            advisor = User(
                username='advisor',
                password_hash=generate_password_hash('advisor123'),
                role='batch advisor',
                name='Batch Advisor',
                email='advisor@comsats.edu.pk',
                is_active=True
            )
            db.session.add(advisor)
            db.session.commit()
        
        # Initialize sample courses if empty
        if Course.query.count() == 0:
            cs_dept = Department.query.filter_by(code='CS').first()
            math_dept = Department.query.filter_by(code='MATH').first()
            eng_dept = Department.query.filter_by(code='ENG').first()
            
            courses = []
            if cs_dept:
                courses.extend([
                    Course(code='CS101', name='Introduction to Computer Science', department_id=cs_dept.id, credit_hours=3),
                    Course(code='CS102', name='Programming Fundamentals', department_id=cs_dept.id, credit_hours=3),
                    Course(code='CS201', name='Data Structures', department_id=cs_dept.id, credit_hours=3),
                ])
            if math_dept:
                courses.extend([
                    Course(code='MATH101', name='Calculus I', department_id=math_dept.id, credit_hours=3),
                    Course(code='MATH102', name='Linear Algebra', department_id=math_dept.id, credit_hours=3),
                ])
            if eng_dept:
                courses.extend([
                    Course(code='ENG101', name='English Composition', department_id=eng_dept.id, credit_hours=3),
                ])
            
            for course in courses:
                db.session.add(course)
            db.session.commit()
        
        # Initialize batch-subject assignments and course-teacher assignments if empty
        if BatchSubject.query.count() == 0:
            cs_dept = Department.query.filter_by(code='CS').first()
            math_dept = Department.query.filter_by(code='MATH').first()
            eng_dept = Department.query.filter_by(code='ENG').first()
            
            # Get Fall 2024 batch for CS
            if cs_dept:
                cs_fall_batch = Batch.query.filter_by(department_id=cs_dept.id, name='Fall 2024').first()
                if cs_fall_batch:
                    cs101 = Course.query.filter_by(code='CS101').first()
                    cs102 = Course.query.filter_by(code='CS102').first()
                    if cs101:
                        db.session.add(BatchSubject(batch_id=cs_fall_batch.id, course_id=cs101.id, is_required=True))
                    if cs102:
                        db.session.add(BatchSubject(batch_id=cs_fall_batch.id, course_id=cs102.id, is_required=True))
            
            # Get Fall 2024 batch for MATH
            if math_dept:
                math_fall_batch = Batch.query.filter_by(department_id=math_dept.id, name='Fall 2024').first()
                if math_fall_batch:
                    math101 = Course.query.filter_by(code='MATH101').first()
                    if math101:
                        db.session.add(BatchSubject(batch_id=math_fall_batch.id, course_id=math101.id, is_required=True))
            
            # Get Fall 2024 batch for ENG (create if needed)
            if eng_dept:
                eng_batch = Batch.query.filter_by(department_id=eng_dept.id).first()
                if not eng_batch:
                    eng_batch = Batch(department_id=eng_dept.id, name='Fall 2024', year=2024, semester='Fall',
                                     start_date=date(2024, 9, 1), end_date=date(2024, 12, 31))
                    db.session.add(eng_batch)
                    db.session.commit()
                
                eng101 = Course.query.filter_by(code='ENG101').first()
                if eng101:
                    db.session.add(BatchSubject(batch_id=eng_batch.id, course_id=eng101.id, is_required=True))
            
            db.session.commit()
        
        # Initialize course-teacher assignments if empty
        if CourseTeacher.query.count() == 0:
            cs_fall_batch = Batch.query.join(Department).filter(Department.code == 'CS', Batch.name == 'Fall 2024').first()
            math_fall_batch = Batch.query.join(Department).filter(Department.code == 'MATH', Batch.name == 'Fall 2024').first()
            eng_fall_batch = Batch.query.join(Department).filter(Department.code == 'ENG', Batch.name == 'Fall 2024').first()
            
            teacher1 = Teacher.query.filter_by(employee_id='EMP001').first()
            teacher2 = Teacher.query.filter_by(employee_id='EMP002').first()
            teacher3 = Teacher.query.filter_by(employee_id='EMP003').first()
            teacher4 = Teacher.query.filter_by(employee_id='EMP004').first()
            
            # Assign teachers to batch-subjects
            if cs_fall_batch:
                cs101_bs = BatchSubject.query.join(Course).filter(BatchSubject.batch_id == cs_fall_batch.id, Course.code == 'CS101').first()
                cs102_bs = BatchSubject.query.join(Course).filter(BatchSubject.batch_id == cs_fall_batch.id, Course.code == 'CS102').first()
                
                # Get section A for CS batch
                cs_section_a = Section.query.filter_by(batch_id=cs_fall_batch.id, name='A').first()
                
            teacher2 = Teacher.query.filter_by(employee_id='EMP002').first()

