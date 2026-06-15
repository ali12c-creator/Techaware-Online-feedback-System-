# TechAware — AI-Based University Feedback System

> An intelligent, automated web-based student feedback system that collects, analyzes, and presents feedback in real-time using Artificial Intelligence to improve teaching quality.

**COMSATS University Islamabad, Vehari Campus**  
Department of Computer Science | BS Computer Science | 2022–2026

---

## 👨‍💻 Developers

| Name | Registration No |
|------|----------------|
| Ali Ahmad | FA22-BCS-163 |
| Nimra Farooq | FA22-BCS-160 |

**Supervisor:** Sir Rizwan Ali

---

## 🚀 Features

- ✅ **4 Role-Based Portals** — Admin, Teacher, Student, Batch Advisor
- 🤖 **Gemini AI Integration** — Smart teaching improvement suggestions
- 💬 **NLP Sentiment Analysis** — TextBlob (Positive / Negative / Neutral)
- 📧 **Automated Email Notifications** — Sent at lecture end time via Gmail SMTP
- 🔒 **Token-Based Feedback** — One-time secure link (24hr expiry)
- ⚖️ **Attendance-Weighted Rating** — Fair teacher evaluation system
- 📈 **4-Week Performance Trend** — Alerts for declining performance
- 📄 **PDF Report Generation** — Downloadable teacher performance reports

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, Flask |
| Database | SQLite + SQLAlchemy ORM |
| AI Analysis | Google Gemini 1.5 Flash |
| NLP | TextBlob |
| Email | Gmail SMTP |
| Scheduler | APScheduler |
| Frontend | HTML5, CSS3, JavaScript, Jinja2 |
| PDF | ReportLab |

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ali12c-creator/Techaware-Online-feedback-System-.git
cd Techaware-Online-feedback-System-
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the root folder:
```
GEMINI_API_KEY=your_gemini_api_key_here
SMTP_EMAIL=your_gmail@gmail.com
SMTP_PASSWORD=your_app_password
SECRET_KEY=your_secret_key
```

### 5. Run the Application
```bash
python app.py
```

Open browser: `http://127.0.0.1:5000`

---

## 👤 Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@comsats.edu.pk | admin123 |
| Teacher | (auto-generated) | (sent via email) |
| Student | (registration number) | (sent via email) |

---

## 📁 Project Structure

```
TechAware/
├── app.py                  # Main Flask application
├── models.py               # Database models (SQLAlchemy)
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates (Jinja2)
├── static/                 # CSS, JS, images
├── instance/               # SQLite database
└── README.md
```

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| Lines of Code | 3,701 |
| API Routes | 76 |
| Database Tables | 14 |
| HTML Templates | 15 |
| Use Cases | 31 |

---

## 🔒 Security Features

- bcrypt password hashing
- CSRF protection
- Session-based authentication
- Role-Based Access Control (RBAC)
- One-time token feedback links

---

## 📄 License

This project is developed for academic purposes at COMSATS University Islamabad.

---

*TechAware — Transforming student feedback into actionable teaching insights using AI* 🎓
