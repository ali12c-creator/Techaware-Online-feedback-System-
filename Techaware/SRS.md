# Software Requirements Specification (SRS)
## TechAware AI-Based Feedback System

**Version:** 1.0  
**Date:** 2024  
**Project:** FYP - Final Year Project  
**Institution:** COMSATS University Islamabad Vehari

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features](#3-system-features)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [System Requirements](#5-system-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [User Requirements](#7-user-requirements)

---

## 1. Introduction

### 1.1 Purpose
This document provides a comprehensive Software Requirements Specification (SRS) for the TechAware AI-Based Feedback System. This system is designed to facilitate real-time student feedback collection, sentiment analysis, and provide actionable insights to educators for improving their teaching methodologies.

### 1.2 Scope
The TechAware Feedback System is a web-based application that allows:
- Students to submit feedback about lectures in real-time
- Automatic sentiment analysis of feedback using Natural Language Processing (NLP)
- Generation of AI-powered suggestions for teachers based on feedback content
- Teachers and administrators to view comprehensive analytics and statistics
- Automatic email notifications to teachers when new feedback is received
- PDF export functionality for feedback reports

### 1.3 Definitions, Acronyms, and Abbreviations
- **SRS**: Software Requirements Specification
- **NLP**: Natural Language Processing
- **AI**: Artificial Intelligence
- **API**: Application Programming Interface
- **PDF**: Portable Document Format
- **UI/UX**: User Interface/User Experience
- **Flask**: Python web framework
- **TextBlob**: Python library for processing textual data and sentiment analysis

### 1.4 References
- Flask Documentation: https://flask.palletsprojects.com/
- TextBlob Documentation: https://textblob.readthedocs.io/
- ReportLab Documentation: https://www.reportlab.com/docs/reportlab-userguide.pdf

### 1.5 Overview
This document is organized into sections covering system features, external interfaces, system requirements, and user requirements. Each section provides detailed specifications for the TechAware Feedback System.

---

## 2. Overall Description

### 2.1 Product Perspective
The TechAware Feedback System is a standalone web application built using Flask framework. It operates as a three-tier architecture:

1. **Presentation Layer**: HTML/CSS/JavaScript frontend templates
2. **Application Layer**: Python Flask backend with business logic
3. **Data Layer**: In-memory data storage (can be extended to database)

### 2.2 Product Functions
The system provides the following major functions:

1. **Student Feedback Collection**
   - Online feedback form submission
   - Student information capture (name, registration number, section)
   - Multi-type feedback (text, rating, lecture type)

2. **Sentiment Analysis**
   - Automatic sentiment classification (Positive/Negative/Neutral)
   - Polarity and subjectivity scoring
   - Real-time feedback categorization

3. **AI-Powered Suggestions**
   - Content-based recommendation generation
   - Keyword-based suggestion extraction
   - Contextual teaching improvement tips

4. **Analytics Dashboard**
   - Visual statistics and charts
   - Feedback trend analysis
   - Real-time data updates

5. **Notification System**
   - Email alerts to teachers
   - Automatic feedback summaries
   - Dashboard statistics inclusion

6. **Report Generation**
   - PDF export functionality
   - Formatted feedback reports
   - Statistical summaries

### 2.3 User Classes and Characteristics

#### 2.3.1 Students
- **Characteristics**: University students attending lectures
- **Technical Skills**: Basic web browsing knowledge
- **Responsibilities**: Submit honest feedback about lectures
- **Access**: Public access to feedback form (no authentication required)

#### 2.3.2 Teachers/Instructors
- **Characteristics**: Educators teaching courses
- **Technical Skills**: Basic computer literacy
- **Responsibilities**: Review feedback, access analytics, improve teaching methods
- **Access**: Admin dashboard with login credentials

#### 2.3.3 Administrators
- **Characteristics**: System administrators or department heads
- **Technical Skills**: Advanced technical knowledge
- **Responsibilities**: Manage system, view all feedback, export reports
- **Access**: Full administrative access with login credentials

### 2.4 Operating Environment
- **Server**: Flask development server (can be deployed to production server)
- **Client**: Modern web browsers (Chrome, Firefox, Safari, Edge)
- **Operating System**: Cross-platform (Windows, Linux, macOS)
- **Python Version**: Python 3.7 or higher
- **Internet Connection**: Required for email functionality

### 2.5 Design and Implementation Constraints
- **Framework**: Must use Flask for backend
- **Language**: Python 3.x
- **Frontend**: HTML, CSS, JavaScript (no frameworks required)
- **Data Storage**: Currently in-memory (global dictionary), can be migrated to database
- **Email Service**: Gmail SMTP service (configurable)

### 2.6 Assumptions and Dependencies
- **Assumptions**:
  - Users have stable internet connection
  - Email service credentials are properly configured
  - Students provide honest and constructive feedback
  - Teachers have email access for notifications

- **Dependencies**:
  - Flask framework installation
  - TextBlob library for sentiment analysis
  - ReportLab library for PDF generation
  - smtplib (Python standard library) for email
  - Chart.js CDN for visualization

---

## 3. System Features

### 3.1 Student Feedback Submission (FR-1)

#### 3.1.1 Description and Priority
**Priority: High**  
Students can submit feedback through an intuitive web form interface.

#### 3.1.2 Functional Requirements

**FR-1.1: Feedback Form Display**
- The system shall display a feedback form with the following fields:
  - Student Name (required, text input)
  - Registration Number (required, text input)
  - Section Selection (required, dropdown: A, B, C)
  - Lecture Type (required, radio buttons: Theory, Practical, Seminar)
  - Rating (required, 5-star rating system)
  - Positive Aspects (optional, checkboxes: Clarity, Engagement, Examples, Pace)
  - Feedback Text (required, minimum 10 characters, textarea)

**FR-1.2: Form Validation**
- The system shall validate all required fields before submission
- The system shall ensure feedback text is at least 10 characters long
- The system shall require a rating selection (1-5 stars)
- The system shall display appropriate error messages for validation failures

**FR-1.3: Feedback Submission**
- The system shall accept feedback via POST request to `/submit_feedback` endpoint
- The system shall process feedback data in JSON format
- The system shall return success/error response in JSON format

**FR-1.4: Feedback Enhancement**
- The system shall automatically append lecture type to feedback text
- The system shall automatically append selected positive aspects
- The system shall automatically append rating to feedback text

**FR-1.5: User Feedback Display**
- The system shall display submission result to the student
- The system shall show sentiment analysis result (emoji and text)
- The system shall display confidence score (polarity percentage)
- The system shall show email notification status
- The system shall auto-clear form after successful submission (3 seconds delay)

### 3.2 Sentiment Analysis (FR-2)

#### 3.2.1 Description and Priority
**Priority: High**  
Automatic sentiment analysis of student feedback using NLP techniques.

#### 3.2.2 Functional Requirements

**FR-2.1: Text Processing**
- The system shall use TextBlob library to analyze feedback text
- The system shall calculate polarity score (range: -1.0 to +1.0)
- The system shall calculate subjectivity score (range: 0.0 to 1.0)

**FR-2.2: Sentiment Classification**
- The system shall classify feedback as:
  - **Positive (Understood)**: If polarity > 0.1
  - **Negative (Not Understood)**: If polarity < -0.1
  - **Neutral**: If -0.1 ≤ polarity ≤ 0.1

**FR-2.3: Sentiment Display**
- The system shall display sentiment with emoji:
  - 😊 for Positive/Understood
  - 😞 for Negative/Not Understood
  - 😐 for Neutral

**FR-2.4: Statistical Tracking**
- The system shall increment appropriate counter:
  - `understood` counter for positive feedback
  - `not_understood` counter for negative feedback
  - `neutral` counter for neutral feedback

**FR-2.5: Feedback Storage**
- The system shall store each feedback entry with:
  - Unique ID (auto-increment)
  - Student information (name, registration, section)
  - Original feedback text
  - Calculated sentiment
  - Polarity and subjectivity scores
  - Timestamp (YYYY-MM-DD HH:MM:SS format)

### 3.3 AI-Powered Suggestions (FR-3)

#### 3.3.1 Description and Priority
**Priority: Medium**  
Generate contextual suggestions for teachers based on feedback content.

#### 3.3.2 Functional Requirements

**FR-3.1: Keyword-Based Analysis**
- The system shall analyze feedback text for specific keywords:
  - Speed-related: "fast", "speed", "quick", "rush", "jaldi"
  - Confusion-related: "confusing", "confused", "unclear", "nahi", "samajh"
  - Example-related: "practical", "example", "real"
  - Visual-related: "diagram", "visual", "picture"
  - Engagement-related: "interesting", "engaging", "fun", "acha"

**FR-3.2: Suggestion Generation for Negative Feedback**
- If sentiment is "Not Understood", the system shall generate suggestions:
  - "💡 Slow down the pace and use more examples" (if speed keywords found)
  - "💡 Break complex concepts into smaller parts" (if confusion keywords found)
  - "💡 Include more real-world examples" (if example keywords found)
  - "💡 Use more diagrams and visual aids" (if visual keywords found)
  - "💡 Consider using interactive teaching methods" (default if no keywords match)

**FR-3.3: Suggestion Generation for Positive Feedback**
- If sentiment is "Understood", the system shall generate suggestions:
  - "✨ Great job! Keep this teaching approach" (always)
  - "✨ Continue with engaging techniques" (if engagement keywords found)

**FR-3.4: Suggestion Generation for Neutral Feedback**
- If sentiment is "Neutral", the system shall generate:
  - "💭 Ask for more specific feedback"

**FR-3.5: Suggestion Storage**
- The system shall store suggestions array with each feedback entry
- The system shall display suggestions in dashboard and email notifications

### 3.4 Email Notification System (FR-4)

#### 3.4.1 Description and Priority
**Priority: Medium**  
Automatic email notifications to teachers when feedback is received.

#### 3.4.2 Functional Requirements

**FR-4.1: Email Configuration**
- The system shall use Gmail SMTP service (smtp.gmail.com, port 587)
- The system shall support TLS encryption (STARTTLS)
- The system shall use pre-configured sender email and password/app password

**FR-4.2: Email Composition**
- The system shall compose email with:
  - **Subject**: "New Feedback - [Sentiment]"
  - **Recipient**: Pre-configured teacher email address
  - **Body**: Formatted text including:
    - Student information (name, registration, section)
    - Feedback text
    - Sentiment analysis result with emoji
    - Polarity score
    - AI-generated suggestions (formatted as bullet points)
    - Current dashboard statistics (understood/not understood/neutral counts)
    - Dashboard link

**FR-4.3: Email Sending**
- The system shall attempt to send email after each feedback submission
- The system shall handle email sending errors gracefully
- The system shall return email status (success/failed) in API response

**FR-4.4: Email Status Reporting**
- The system shall display email status to student:
  - "✅ Email sent!" on success
  - "⚠️ Email failed" on failure
- The system shall log email errors (currently to console)

### 3.5 Teacher Dashboard (FR-5)

#### 3.5.1 Description and Priority
**Priority: High**  
Comprehensive analytics dashboard for teachers to view feedback statistics.

#### 3.5.2 Functional Requirements

**FR-5.1: Dashboard Access**
- The system shall provide dashboard at `/dashboard` route
- The system shall display dashboard without authentication (can be secured)

**FR-5.2: Statistics Display**
- The system shall display four statistic boxes:
  - **Understood**: Count of positive feedback (green theme)
  - **Not Understood**: Count of negative feedback (red theme)
  - **Neutral**: Count of neutral feedback (yellow theme)
  - **Total**: Total number of feedback entries (green theme)

**FR-5.3: Chart Visualization**
- The system shall display doughnut chart using Chart.js
- The chart shall show distribution of feedback sentiments
- The chart shall use color scheme:
  - Green (#28a745) for Understood
  - Red (#dc3545) for Not Understood
  - Yellow (#ffc107) for Neutral
- The chart shall update automatically when data changes

**FR-5.4: AI Suggestions Display**
- The system shall display all unique AI-generated suggestions
- The system shall limit display to 10 most recent suggestions
- The system shall show suggestions in styled cards
- The system shall indicate if no suggestions are available

**FR-5.5: Feedback List Display**
- The system shall display all feedback entries in reverse chronological order (newest first)
- Each feedback entry shall display:
  - Student name, registration number, section
  - Timestamp
  - Feedback text (in quotes, italic style)
  - Sentiment badge (color-coded)
  - Polarity score
  - AI-generated suggestions
  - Delete button

**FR-5.6: Color-Coding**
- Feedback items shall be color-coded by sentiment:
  - Green left border for "Understood"
  - Red left border for "Not Understood"
  - Yellow left border for "Neutral"

**FR-5.7: Dashboard Controls**
- The system shall provide buttons:
  - **Export PDF**: Generate and download PDF report
  - **New Feedback**: Navigate to feedback form
  - **Refresh**: Manually refresh dashboard data
  - **Admin**: Navigate to admin login page
  - **Clear All**: Delete all feedback (with confirmation)

**FR-5.8: Auto-Refresh**
- The system shall automatically refresh dashboard data every 5 seconds
- The system shall fetch data from `/get_feedback_summary` endpoint

### 3.6 Admin Authentication (FR-6)

#### 3.6.1 Description and Priority
**Priority: Medium**  
Admin login system for dashboard access.

#### 3.6.2 Functional Requirements

**FR-6.1: Admin Login Page**
- The system shall provide admin login page at `/admin` route
- The page shall display login form with:
  - Username input field
  - Password input field (masked)
  - Login button
  - Demo credentials information box

**FR-6.2: Credential Management**
- The system shall support multiple admin users:
  - Username: "admin", Password: "admin123"
  - Username: "teacher", Password: "teacher123"
- The system shall store credentials in application memory (hardcoded dictionary)

**FR-6.3: Authentication Process**
- The system shall accept login via POST request to `/admin_login` endpoint
- The system shall validate username and password
- The system shall return JSON response:
  - `success: true` with message on valid credentials
  - `success: false` with error message on invalid credentials

**FR-6.4: Login Success Action**
- Upon successful login, the system shall:
  - Display success message
  - Redirect to dashboard after 1 second delay
  - Store login state in session (currently redirect only, no session management)

**FR-6.5: Input Validation**
- The system shall validate that username and password fields are not empty
- The system shall display appropriate error messages
- The system shall clear password field on failed login attempt

**FR-6.6: Keyboard Support**
- The system shall support Enter key to submit login form
- The system shall support Enter key in username field to focus password field

### 3.7 Feedback Management (FR-7)

#### 3.7.1 Description and Priority
**Priority: Medium**  
CRUD operations for feedback management.

#### 3.7.2 Functional Requirements

**FR-7.1: Delete Single Feedback**
- The system shall provide delete functionality for individual feedback entries
- The system shall require confirmation before deletion
- The system shall decrement appropriate sentiment counter on deletion
- The system shall remove feedback entry from storage
- The system shall return success/error response

**FR-7.2: Clear All Feedback**
- The system shall provide functionality to delete all feedback
- The system shall require confirmation dialog (cannot undo warning)
- The system shall reset all counters to zero
- The system shall clear feedback list
- The system shall return success message

**FR-7.3: Feedback Retrieval**
- The system shall provide endpoint `/get_feedback_summary` (GET request)
- The endpoint shall return JSON with:
  - `understood`: Count integer
  - `not_understood`: Count integer
  - `neutral`: Count integer
  - `feedback_list`: Array of all feedback entries

### 3.8 PDF Export Functionality (FR-8)

#### 3.8.1 Description and Priority
**Priority: Low**  
Generate and export feedback reports as PDF documents.

#### 3.8.2 Functional Requirements

**FR-8.1: PDF Generation**
- The system shall use ReportLab library to generate PDF
- The system shall create PDF with A4 page size
- The system shall include:
  - Title: "📊 TechAware Feedback Report"
  - Statistics summary (total feedback, understood, not understood, neutral counts)
  - Table with last 10 feedback entries showing:
    - Name (truncated to 15 characters)
    - Registration (truncated to 10 characters)
    - Section
    - Sentiment (truncated to 12 characters)
    - Polarity score

**FR-8.2: PDF Styling**
- The system shall use custom styling:
  - Title: 24pt font, green color (#28a745), centered
  - Table header: Green background, white text, bold
  - Table body: Beige background, black text
  - Table borders: Black grid lines

**FR-8.3: PDF Download**
- The system shall provide endpoint `/export_pdf` (GET request)
- The system shall return PDF file with:
  - MIME type: `application/pdf`
  - Download name: `feedback_report.pdf`
  - Attachment disposition (download, not inline)

**FR-8.4: PDF Access**
- The system shall allow PDF download via dashboard button click
- The system shall handle PDF generation errors gracefully

---

## 4. External Interface Requirements

### 4.1 User Interfaces

#### 4.1.1 Student Feedback Page
- **URL**: `/` (root route)
- **Design**: Modern, gradient background (purple-blue), responsive
- **Components**:
  - Banner section with logo and title
  - Image slider with 7 gallery images (auto-animated)
  - Feedback form (white background card)
  - Footer with institution name

#### 4.1.2 Teacher Dashboard
- **URL**: `/dashboard`
- **Design**: Dark theme, modern UI with gradient headers
- **Components**:
  - Header with title and subtitle
  - Control buttons bar
  - Statistics cards (4 boxes)
  - Chart container (doughnut chart)
  - AI suggestions panel
  - Feedback list with individual entries

#### 4.1.3 Admin Login Page
- **URL**: `/admin`
- **Design**: Centered login card, gradient background
- **Components**:
  - Login form
  - Demo credentials information box
  - Success/error message display

### 4.2 Hardware Interfaces
- **Server**: Standard web server hardware (CPU, RAM, storage)
- **Client**: Any device with web browser (PC, laptop, tablet, smartphone)
- **Network**: Internet connection for email functionality

### 4.3 Software Interfaces

#### 4.3.1 Flask Framework
- **Version**: Flask 2.x or compatible
- **Purpose**: Web application framework
- **Routes**: 7 endpoints defined

#### 4.3.2 TextBlob Library
- **Purpose**: Sentiment analysis and NLP
- **Methods Used**:
  - `TextBlob(text)` - Initialize text object
  - `.sentiment.polarity` - Get polarity score (-1 to +1)
  - `.sentiment.subjectivity` - Get subjectivity score (0 to 1)

#### 4.3.3 smtplib (Python Standard Library)
- **Purpose**: Email sending
- **Protocol**: SMTP with TLS
- **Server**: smtp.gmail.com, Port: 587

#### 4.3.4 ReportLab Library
- **Purpose**: PDF generation
- **Components Used**:
  - `SimpleDocTemplate` - PDF document template
  - `Table` - Table creation
  - `Paragraph` - Text formatting
  - `TableStyle` - Table styling
  - `ParagraphStyle` - Paragraph styling

#### 4.3.5 Chart.js (CDN)
- **Purpose**: Data visualization
- **Version**: Latest from CDN
- **Chart Type**: Doughnut chart
- **Location**: External CDN (jsdelivr.net)

### 4.4 Communication Interfaces

#### 4.4.1 HTTP/HTTPS
- **Protocol**: HTTP (development), HTTPS (production recommended)
- **Methods**: GET, POST
- **Content-Type**: `application/json` for API, `text/html` for pages

#### 4.4.2 Email (SMTP)
- **Protocol**: SMTP with STARTTLS
- **Server**: smtp.gmail.com
- **Port**: 587
- **Authentication**: Username and app password

### 4.5 API Endpoints

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/` | GET | Feedback form page | None | HTML page |
| `/dashboard` | GET | Teacher dashboard | None | HTML page |
| `/admin` | GET | Admin login page | None | HTML page |
| `/submit_feedback` | POST | Submit feedback | JSON: name, reg, section, feedback | JSON: message, sentiment, polarity, email_status, suggestions |
| `/get_feedback_summary` | GET | Get all feedback data | None | JSON: understood, not_understood, neutral, feedback_list |
| `/admin_login` | POST | Admin authentication | JSON: username, password | JSON: success, message |
| `/delete_feedback/<id>` | POST | Delete single feedback | None | JSON: success, message |
| `/clear_feedback` | POST | Delete all feedback | None | JSON: message |
| `/export_pdf` | GET | Generate PDF report | None | PDF file |

---

## 5. System Requirements

### 5.1 Functional Requirements Summary

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-1 | Student Feedback Submission | High | Implemented |
| FR-2 | Sentiment Analysis | High | Implemented |
| FR-3 | AI-Powered Suggestions | Medium | Implemented |
| FR-4 | Email Notification System | Medium | Implemented |
| FR-5 | Teacher Dashboard | High | Implemented |
| FR-6 | Admin Authentication | Medium | Implemented |
| FR-7 | Feedback Management | Medium | Implemented |
| FR-8 | PDF Export Functionality | Low | Implemented |

### 5.2 Data Requirements

#### 5.2.1 Feedback Data Structure
```json
{
  "understood": 0,
  "not_understood": 0,
  "neutral": 0,
  "feedback_list": [
    {
      "id": 1,
      "name": "Student Name",
      "reg": "Registration Number",
      "section": "A",
      "text": "Feedback text",
      "sentiment": "✅ UNDERSTOOD",
      "polarity": 0.75,
      "subjectivity": 0.65,
      "suggestions": ["Suggestion 1", "Suggestion 2"],
      "timestamp": "2024-01-01 12:00:00"
    }
  ]
}
```

#### 5.2.2 Admin Credentials Structure
```python
{
  "admin": "admin123",
  "teacher": "teacher123"
}
```

### 5.3 Performance Requirements

#### 5.3.1 Response Time
- Page load time: < 2 seconds
- API response time: < 1 second
- Sentiment analysis time: < 0.5 seconds
- Email sending time: < 3 seconds (asynchronous preferred in production)

#### 5.3.2 Throughput
- Support at least 100 concurrent users
- Handle at least 50 feedback submissions per minute

#### 5.3.3 Scalability
- System designed for horizontal scaling
- Data storage can be migrated to database (PostgreSQL, MySQL, MongoDB)

### 5.4 Security Requirements

#### 5.4.1 Authentication
- Admin credentials stored securely (currently hardcoded, should use hashed passwords)
- Session management recommended for production
- HTTPS recommended for production deployment

#### 5.4.2 Data Protection
- Email credentials should be stored in environment variables (not hardcoded)
- Input validation and sanitization required
- Protection against SQL injection (when database is integrated)
- Protection against XSS attacks (input sanitization)

#### 5.4.3 Access Control
- Public access to feedback form (students)
- Restricted access to dashboard (authentication required)
- Role-based access control recommended for future versions

---

## 6. Non-Functional Requirements

### 6.1 Usability
- **Ease of Use**: Intuitive interface, minimal learning curve
- **Accessibility**: Responsive design, works on mobile devices
- **User Feedback**: Clear success/error messages
- **Visual Design**: Modern, clean, professional appearance

### 6.2 Reliability
- **Availability**: System should be available 99% of the time
- **Error Handling**: Graceful error handling, user-friendly error messages
- **Data Integrity**: Feedback data should not be lost (currently in-memory, needs persistence)

### 6.3 Maintainability
- **Code Quality**: Well-structured, commented code
- **Modularity**: Separate routes, functions, and templates
- **Documentation**: Code comments and documentation

### 6.4 Portability
- **Cross-Platform**: Works on Windows, Linux, macOS
- **Browser Compatibility**: Works on Chrome, Firefox, Safari, Edge
- **Python Version**: Compatible with Python 3.7+

### 6.5 Efficiency
- **Resource Usage**: Minimal memory and CPU usage
- **Code Efficiency**: Optimized algorithms for sentiment analysis
- **Network Efficiency**: Minimal data transfer, compressed responses where possible

---

## 7. User Requirements

### 7.1 Student User Requirements

#### 7.1.1 As a student, I should be able to:
- Access the feedback form easily through a web browser
- Submit feedback without creating an account or logging in
- See immediate confirmation of feedback submission
- View the sentiment analysis result of my feedback
- Know that my feedback has been sent to the teacher via email

#### 7.1.2 Student Workflow:
1. Open web browser
2. Navigate to feedback form URL
3. Fill in personal information (name, registration, section)
4. Select lecture type and provide rating
5. Write feedback text (minimum 10 characters)
6. Click "Submit Feedback" button
7. View submission confirmation and sentiment result
8. Form auto-clears after 3 seconds

### 7.2 Teacher User Requirements

#### 7.2.1 As a teacher, I should be able to:
- Access the dashboard with login credentials
- View real-time statistics of student feedback
- See visual representation of feedback distribution (charts)
- View individual feedback entries with details
- Read AI-generated suggestions for improving teaching
- Export feedback reports as PDF
- Delete individual feedback entries
- Clear all feedback data (if needed)

#### 7.2.2 Teacher Workflow:
1. Navigate to admin login page
2. Enter username and password
3. Access dashboard after successful login
4. View statistics and charts
5. Review individual feedback entries
6. Read AI suggestions
7. Export PDF report (optional)
8. Delete unwanted feedback (optional)
9. Dashboard auto-refreshes every 5 seconds

### 7.3 Administrator User Requirements

#### 7.3.1 As an administrator, I should be able to:
- Access admin panel with credentials
- View all feedback data
- Manage feedback entries
- Export comprehensive reports
- Clear all data when needed
- Access the same features as teachers

#### 7.3.2 Administrator Workflow:
- Similar to teacher workflow with additional administrative privileges

---

## Appendix A: Glossary

- **Sentiment Analysis**: Process of determining emotional tone of text (positive, negative, neutral)
- **Polarity**: Sentiment score ranging from -1 (negative) to +1 (positive)
- **Subjectivity**: Measure of how opinion-based text is (0 = objective, 1 = subjective)
- **NLP**: Natural Language Processing - field of AI concerned with language understanding
- **SMTP**: Simple Mail Transfer Protocol - standard for email transmission
- **CDN**: Content Delivery Network - distributed network for delivering web content

## Appendix B: Future Enhancements

1. **Database Integration**: Migrate from in-memory storage to persistent database
2. **Advanced Analytics**: Trend analysis, time-series charts, comparative analysis
3. **Multi-language Support**: Support for Urdu and other languages in sentiment analysis
4. **Advanced AI**: Machine learning models for better suggestion generation
5. **Notification Preferences**: Teachers can configure notification settings
6. **Feedback Categories**: Categorize feedback by topic/subject
7. **Export Options**: Excel, CSV export in addition to PDF
8. **User Management**: Registration, profiles, password management
9. **Response System**: Teachers can respond to student feedback
10. **Reporting Schedules**: Automated scheduled reports via email

---

**Document End**

