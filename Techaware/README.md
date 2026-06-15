# 📚 Student Feedback Portal - TechAware Feedback System

A comprehensive web-based student feedback management system designed to collect, analyze, and manage student feedback for lectures. The system automatically sends notifications to students after lectures and provides detailed analytics to teachers and administrators.

---

## 🌟 Project Overview

The **Student Feedback Portal** is an automated feedback collection system that enables educational institutions to:
- Collect student feedback after each lecture automatically
- Analyze feedback using AI-powered sentiment analysis
- Generate actionable insights for teachers
- Track teacher performance over time
- Maintain attendance and feedback records
- Send automated email notifications

### Key Features
- ⏰ **Automatic Message Sending**: Configurable timing (after lecture, weekly, or monthly)
- 📊 **Real-time Analytics**: Sentiment analysis and performance metrics
- 📧 **Email Notifications**: Automated email system with SMTP integration
- 🔐 **Role-based Access Control**: Admin, Teacher, Student, and Batch Advisor sections
- 📝 **Attendance Integration**: Only present students receive feedback requests

---

## 🎯 System Architecture

The system consists of **4 main sections**:

### 1. 👨‍💼 **Admin Section**
Complete system management with full CRUD operations.

### 2. 👨‍🏫 **Teacher Section**
Dashboard for viewing feedback, marking attendance, and accessing teaching insights.

### 3. 👨‍🎓 **Student Section**
Interface for submitting feedback after lectures.

### 4. 📋 **Batch Advisor Section**
Overview and monitoring of batch performance and teacher statistics.

---

## 📋 Admin Section Features

### Full CRUD Operations
Admin has complete control over all system entities with Create, Read, Update, and Delete capabilities.

### 1. **Teacher Management**
- Teacher Name
- Teacher Subject
- Email
- Password
- Department
- Designation

### 2. **Batch Management**
- Department
- Batch Name
- Year
- Semester
- Start Date
- End Date

### 3. **Section Management**
- Department
- Batch
- Section Name
- Capacity

### 4. **Subject/Course Management**
- Course ID
- Course Name
- Department
- Credit Hours
- Description

### 5. **Assign Subject to Batch**
- Department
- Batch
- Subject

### 6. **Assign Teacher**
- Department
- Batch
- Subject
- Course
- Section
- Lecture Type (Theory/Practical/Seminar)

### 7. **User Management**
- Name
- Email
- Password
- Role (Admin/Teacher/Student/Batch Advisor)

### 8. **Feedback Management Dashboard**
Summary table displaying:
- **ID**: Feedback identifier
- **Student**: Student name and registration number
- **Course**: Course code and name
- **Teacher**: Teacher name
- **Sentiment**: Feedback sentiment (Positive/Negative/Neutral)
- **Rating**: Overall rating (1-5 stars)
- **Status**: Approval status
- **Date**: Submission date
- **Actions**: Edit/Delete/Approve/Reject options

### 9. **SMTP Configuration**
System automatically sends emails using SMTP configuration:
- Email server setup
- Port configuration
- Sender email
- App password for secure authentication
- Automated emails for:
  - Verification emails
  - Password reset
  - Notification emails
  - Feedback reminders

### 10. **Analytics & Reports**
- System-wide statistics
- Teacher performance comparison
- Department-wise analytics
- Custom report generation
- Export functionality (PDF/Excel/CSV)

### 11. **Timetable Management**
- Create/Edit/Delete timetable entries
- Conflict detection (teacher, room, section)
- Semester-wise scheduling
- Room availability checking

---

## 👤 User Account Creation Flow

The correct flow is this:

The admin has a list of which students and teachers are there in this semester.

Admin will add their Email and Role (Student/Teacher) from his panel.

The system will create their account.

When the user (student) comes for the first time, he will "login" with the email which was sent by the admin.

---

## 👨‍🎓 Student Section Features

### Student Feedback Form
The feedback form collects comprehensive student experience:

#### Form Fields:
- **Section Selection**: Student's section
- **Course Selection**: Course being evaluated
- **Teacher Selection**: Instructor for the lecture
- **Lecture Type**: Theory/Practical/Seminar

#### Feedback Components:
- **Quality Rating**: Rate lecture quality (1-5 stars)
- **Structured Ratings**:
  - Teaching Clarity
  - Punctuality
  - Course Material Quality
  - Communication Skills
  - Overall Satisfaction
- **Text Feedback**: Written feedback about:
  - What was good
  - What could be improved
  - General comments

### Student Login
- **Separate Login Page**: Dedicated student login interface
- **Login Method**: Email-based authentication
- **Email Integration**: Email address used for:
  - Login authentication
  - Receiving popup/notification messages
  - Feedback reminders

### Automatic Notifications
- Students receive automatic messages after lectures
- Only **present students** (marked by teacher) receive feedback requests
- Notification timing configurable:
  - Immediately after lecture
  - Weekly summary
  - Monthly summary

---

## 👨‍🏫 Teacher Section Features

### Teacher Dashboard
Comprehensive dashboard showing:

#### Feedback Summary
- All student feedback for teacher's courses
- Sentiment analysis results
- Rating breakdowns
- Performance trends over time

#### AI-Powered Insights
- **Teaching Improvement Suggestions**: AI model analyzes feedback and suggests:
  - How to improve teaching methods
  - Areas of strength
  - Areas needing attention
- Actionable recommendations for better student engagement

#### Attendance Management
- Mark student attendance during/after lectures
- Attendance display and tracking
- Only marked students receive feedback emails

#### Self-Profile Management
Teachers can add/update their own details:
- Name
- Course(s)
- Department
- Batch
- Email ID
- Other relevant information

#### Detailed Summary View
Beautiful, comprehensive summary showing:
- Overall feedback statistics
- Student ratings distribution
- Sentiment breakdown
- Performance metrics
- Improvement suggestions
- Historical trends

### Access Control
- **Secure Access**: Only authorized users can access
- **Role-based Permissions**: Teachers can only access their own data
- **Email & Password Authentication**: Secure login system

### Automatic Email Notifications
After feedback submission and analysis:
- **Automatic Email** sent to teacher with:
  - Feedback summary
  - Direct link to teacher dashboard
  - Performance insights
- Teacher can click link and login with their credentials

---

## 📋 Batch Advisor Section Features

### Batch Advisor Dashboard
- **Separate Section**: Dedicated batch advisor interface
- **Login**: Email and password authentication
- **Summary View**: Overview of batch performance

### Automated Alerts
If teacher's feedback performance is below **50% for 2 consecutive weeks**:
- **Automatic Email** sent to Batch Advisor
- Alert indicates: "Teacher is not teaching well"
- Enables proactive intervention and support

### Monitoring Features
- Teacher performance tracking
- Batch-wise feedback statistics
- Attendance patterns
- Student engagement metrics

---

## 🔄 Feedback Flow & Workflow

### Complete Feedback Cycle:

1. **Lecture Completion**
   - Teacher conducts lecture
   - Teacher marks attendance (who was present)

2. **Automatic Notification**
   - System automatically sends email/message to **present students only**
   - Message: "Please provide feedback for today's lecture"

3. **Student Feedback Submission**
   - Students access feedback form
   - Fill out ratings and written feedback
   - Submit feedback

4. **Feedback Analysis**
   - System analyzes feedback using AI
   - Generates sentiment analysis
   - Creates performance metrics
   - Produces teaching improvement suggestions

5. **Teacher Notification**
   - Automatic email sent to teacher
   - Contains feedback summary
   - Includes link to teacher dashboard
   - Teacher can login and view detailed analysis

6. **Performance Monitoring**
   - System tracks teacher performance over time
   - If performance drops below 50% for 2 weeks
   - Automatic alert sent to Batch Advisor

---

## 🛠️ Technical Features

### Backend Technology
- **Framework**: Flask (Python)
- **Database**: SQLite/PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login with password hashing
- **Email**: SMTP integration for automated emails

### Frontend Technology
- **HTML5/CSS3**: Modern, responsive design
- **JavaScript**: Dynamic user interface
- **AJAX**: Asynchronous data loading
- **Bootstrap**: UI framework for styling

### AI & Analytics
- **Sentiment Analysis**: TextBlob/NLTK for feedback analysis
- **Performance Metrics**: Automated calculation of teaching effectiveness
- **Recommendation Engine**: AI-powered teaching improvement suggestions

### Security Features
- Password hashing (bcrypt)
- Session management
- Role-based access control
- CSRF protection
- SQL injection prevention

---

## 📧 Email System

### SMTP Configuration
The system uses SMTP for automated email delivery:

```
SMTP Server Configuration:
- Server: smtp.gmail.com (or custom)
- Port: 587 (TLS) or 465 (SSL)
- Sender Email: Configured admin email
- App Password: Secure authentication
```

### Email Types Sent:
1. **Student Notifications**: Feedback request after lectures
2. **Teacher Notifications**: Feedback summary and dashboard link
3. **Batch Advisor Alerts**: Low performance warnings
4. **Password Reset**: Account recovery emails
5. **Verification Emails**: Account verification
6. **System Notifications**: Important updates

---

## 📁 Project File Structure

```
FYP_PROJECT/
│
├── app.py                          # Main Flask application file
├── models.py                       # Database models (SQLAlchemy)
├── database.py                     # Database initialization and migration
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation (this file)
│
├── instance/                       # Instance folder (database storage)
│   └── techaware.db               # SQLite database file
│
├── templates/                      # HTML templates (Jinja2)
│   ├── home.html                  # Landing page
│   ├── admin.html                 # Admin login page
│   ├── admin_manage.html          # Admin management panel
│   ├── dashboard.html             # Teacher dashboard
│   ├── student_login.html         # Student login page
│   ├── student_dashboard.html     # Student dashboard
│   └── feedback.html              # Feedback form
│
├── static/                         # Static files (CSS, JS, images)
│   ├── style.css                  # Main stylesheet
│   ├── modern-style.css           # Modern UI styles
│   ├── enhanced-style.css         # Enhanced styles
│   ├── admin_manage.js            # Admin panel JavaScript
│   ├── enhanced-utils.js          # Utility JavaScript functions
│   ├── logo.png                   # Application logo
│   ├── logo.jpg                   # Logo alternative
│   ├── banner_hd.jpg              # Banner image
│   ├── university.jpg             # University image
│   └── gal*.jpeg                  # Gallery images (gal1-7)
│
├── __pycache__/                   # Python cache files (auto-generated)
│
└── Documentation/                  # Project documentation files
    ├── SRS.md                     # Software Requirements Specification
    ├── SYSTEM_REDESIGN.md         # System redesign documentation
    ├── COMPLETE_SYSTEM_DESIGN.md  # Complete system design
    ├── DATABASE_SCHEMA.md         # Database schema documentation
    ├── IMPLEMENTATION_GUIDE.md    # Implementation guide
    ├── IMPLEMENTATION_STATUS.md   # Implementation status tracking
    ├── IMPROVEMENTS.md            # Improvements documentation
    ├── FRONTEND_ENHANCEMENTS.md   # Frontend enhancements
    └── TODO_COMPLETE_SYSTEM.md    # TODO list for complete system
```

### 📂 Directory Descriptions

#### **Root Files**
- **`app.py`**: Main Flask application with all routes, authentication, API endpoints, and business logic
- **`models.py`**: SQLAlchemy database models for all entities (User, Department, Batch, Section, Course, Teacher, Student, Feedback, Timetable, etc.)
- **`database.py`**: Database initialization, schema migration, and default data setup
- **`requirements.txt`**: Python package dependencies required for the project
- **`README.md`**: Complete project documentation

#### **`instance/` Directory**
- Contains instance-specific files (database, configuration)
- **`techaware.db`**: SQLite database file with all application data

#### **`templates/` Directory**
- Jinja2 HTML templates for all web pages
- **`home.html`**: Landing page with navigation and student login form
- **`admin.html`**: Admin/Teacher login page
- **`admin_manage.html`**: Comprehensive admin management panel with all CRUD operations
- **`dashboard.html`**: Teacher dashboard with feedback analytics and insights
- **`student_login.html`**: Student login page
- **`student_dashboard.html`**: Student dashboard with timetable and feedback history
- **`feedback.html`**: Student feedback submission form

#### **`static/` Directory**
- Static assets (CSS, JavaScript, images)
- **CSS Files**:
  - `style.css`: Base stylesheet
  - `modern-style.css`: Modern UI components and responsive design
  - `enhanced-style.css`: Enhanced styling for advanced features
- **JavaScript Files**:
  - `admin_manage.js`: Complete admin panel functionality (CRUD operations, AJAX calls)
  - `enhanced-utils.js`: Utility functions for enhanced features
- **Images**:
  - Logo files: `logo.png`, `logo.jpg`
  - Banner: `banner_hd.jpg`
  - University image: `university.jpg`
  - Gallery images: `gal1.jpeg` through `gal7.jpeg`

#### **Documentation Files**
- **`SRS.md`**: Software Requirements Specification
- **`SYSTEM_REDESIGN.md`**: Complete system redesign documentation
- **`COMPLETE_SYSTEM_DESIGN.md`**: Detailed system design document
- **`DATABASE_SCHEMA.md`**: Database schema and relationships
- **`IMPLEMENTATION_GUIDE.md`**: Step-by-step implementation guide
- **`IMPLEMENTATION_STATUS.md`**: Current implementation status tracking
- **`IMPROVEMENTS.md`**: Planned improvements and enhancements
- **`FRONTEND_ENHANCEMENTS.md`**: Frontend enhancement documentation
- **`TODO_COMPLETE_SYSTEM.md`**: Complete TODO list for system features

---

## 🗄️ Database Schema

### Core Tables:
- **Users**: Admin, Teacher, Student accounts
- **Departments**: Academic departments
- **Batches**: Academic batches/years
- **Sections**: Sections within batches
- **Courses**: Subject/course information
- **Teachers**: Teacher profiles
- **Students**: Student profiles
- **Timetable**: Lecture schedules
- **Feedback**: Student feedback submissions
- **Attendance**: Attendance records
- **CourseTeachers**: Teacher-course assignments
- **BatchSubjects**: Batch-course assignments

---

## 🚀 Installation & Setup

### Prerequisites
```bash
Python 3.8+
pip
virtualenv (recommended)
```

### Installation Steps

1. **Clone Repository**
```bash
git clone <repository-url>
cd FYP_PROJECT
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Database Setup**
```bash
python database.py
```

5. **Configure SMTP**
- Update SMTP settings in admin panel
- Configure email credentials

6. **Run Application**
```bash
python app.py
```

7. **Access Application**
- Open browser: `http://localhost:5000`
- Login with admin credentials

---

## 👥 User Roles & Access

### Admin
- Full system access
- CRUD operations on all entities
- System configuration
- SMTP setup
- Analytics and reports

### Teacher
- View own feedback
- Mark attendance
- Update profile
- Access teaching insights
- View performance metrics

### Student
- Submit feedback
- View own feedback history
- Access timetable
- Update profile

### Batch Advisor
- View batch summaries
- Monitor teacher performance
- Receive low-performance alerts
- Access batch statistics

---

## 📊 Key Modules

1. **User Management**: Complete user lifecycle management
2. **Academic Management**: Departments, Batches, Sections, Courses
3. **Timetable Management**: Lecture scheduling with conflict detection
4. **Feedback Collection**: Structured feedback form with ratings
5. **Sentiment Analysis**: AI-powered feedback analysis
6. **Email Automation**: SMTP-based notification system
7. **Analytics Dashboard**: Real-time statistics and reports
8. **Attendance Tracking**: Integration with feedback system
9. **Performance Monitoring**: Automated alerts and tracking

---

## 🔐 Security

- **Password Hashing**: Bcrypt for secure password storage
- **Session Management**: Secure session handling
- **Role-based Access**: Permissions based on user roles
- **CSRF Protection**: Cross-site request forgery prevention
- **SQL Injection Prevention**: Parameterized queries
- **Email Verification**: Secure email-based authentication

---

## 📈 Future Enhancements

- [ ] Mobile app support
- [ ] Real-time notifications (WebSocket)
- [ ] Advanced analytics with charts
- [ ] Bulk data import/export
- [ ] Multi-language support
- [ ] Advanced AI recommendations
- [ ] Video feedback integration
- [ ] Parent portal access

---

## 🤝 Contributing

This is a Final Year Project (FYP) for academic purposes.

---

## 📝 License

This project is developed as part of academic curriculum.

---

## 👨‍💻 Developer

Developed as part of Final Year Project (FYP)
**TechAware Feedback System**

---

## 📞 Support

For issues or questions, please contact the development team.

---

## 🎓 Academic Purpose

This project is designed for educational institutions to:
- Improve teaching quality through feedback
- Enhance student-teacher communication
- Track and improve academic performance
- Automate feedback collection processes
- Generate actionable insights for continuous improvement

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Active Development

