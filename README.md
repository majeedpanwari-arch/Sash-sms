# Sash SMS — Premium Multi-Tenant SMS Management Panel

![Sash SMS Platform](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![Framework](https://img.shields.io/badge/Framework-Flask-black)
![License](https://img.shields.io/badge/License-Proprietary-red)

**Sash SMS** is a feature-rich, high-performance, multi-tenant SMS management application built with Flask, SQLAlchemy, and a modern high-contrast UI theme. Designed for administrators, agents, and clients to efficiently manage SMS numbers, ranges, CDR reports, access codes, ring subscriptions, and API webhooks.

---

## 🌟 Key Features

### 👑 Role-Based Access Control (RBAC)
- **Administrator**: Complete control over users, agents, clients, SMS ranges, ring tiers, global settings, API configurations, and activity logs.
- **Agent**: Dedicated dashboard to manage numbers, assign numbers to clients, inspect client activity, and configure API/Bot settings.
- **Client**: Client portal to view purchased numbers, incoming SMS messages, CDR reports, and subscription details.
- **Developer**: Tools for inspecting static pages, asset uploads, and system utilities.

### 📱 SMS & Range Management
- Add, assign, release, and monitor phone numbers across multiple ranges.
- Automated number distribution between Agents and Clients.
- CDR (Call Detail Record) log generation and exportable reports.
- Real-time SMS monitoring with session & captcha support.

### 💍 Ring Tier Subscriptions
- Tiered system (e.g., Gold Ring, Silver Ring, Bronze Ring) with customizable limits and pricing.
- Toggle, edit, and audit ring stats per client/agent.

### ⚡ Access Codes & Verification
- Generate single or batch verification codes.
- Export codes to CSV/TXT format.
- Public code verification portal (`/verify`).

### 🛡️ Security & Performance
- Built-in rate limiting per IP for login security.
- Auto-refreshing mathematical captcha to prevent automated bot brute-forcing.
- Session timeout management and user lockout handling.
- Optimized high-contrast dark theme tailored for clarity and accessibility.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.x, Flask, Flask-SQLAlchemy, Flask-Login, Werkzeug
- **Frontend**: HTML5, Vanilla CSS (High-Contrast Design System), Bootstrap, FontAwesome, JavaScript (jQuery)
- **Database**: SQLite (Development) / PostgreSQL or MySQL (Production)
- **Production Server**: Gunicorn / Waitress / Nginx / Docker / Vercel Serverless

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- Python 3.8+ installed on your system.

### 2. Installation & Setup

Clone the repository:
```bash
git clone https://github.com/majeedpanwari-arch/Sash-sms.git
cd Sash-sms
```

Create a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the Application

Start the local server:
```bash
python run.py
```

The application will be accessible at:
👉 **`http://localhost:20168`**

---

## 🔒 Default Admin Credentials

Upon initial database seeding, you can log in with:

- **Username**: `admin`
- **Password**: `admin123`

*(Note: Please change the default admin password in production immediately via the Admin Settings page).*

---

## 📂 Project Structure

```
Sash-sms/
├── app/
│   ├── models/           # SQLAlchemy Data Models (User, SMS, Ring, Activity)
│   ├── routes/           # Blueprint Routes (Admin, Auth, Main, API, Rings, SMS Monitor)
│   ├── static/           # CSS styles, JS scripts, icons, images
│   └── templates/        # HTML templates (Auth, Admin, Main, Developer, Verification)
├── Dockerfile            # Production Docker container configuration
├── docker-compose.yml    # Multi-container orchestration config
├── wsgi.py               # WSGI entrypoint for production servers
├── run.py                # Local development server launcher
├── requirements.txt      # Python dependencies list
├── vercel.json           # Vercel deployment configuration
└── README.md             # Project documentation
```

---

## 🌐 Deployment Options

### Option 1: Hostinger / VPS (Linux with Nginx & Gunicorn)
1. Transfer files to `/var/www/sash-sms`.
2. Configure `.env` with production `SECRET_KEY` and database URI.
3. Setup `systemd` service for Gunicorn.
4. Configure Nginx reverse proxy with SSL certificate (Certbot/Let's Encrypt).

### Option 2: Docker Container
```bash
docker build -t sash-sms .
docker run -d -p 20168:20168 --name sash-sms-app sash-sms
```

### Option 3: Vercel Deployment
The repository includes a ready `vercel.json` file for effortless deployment on Vercel platform.

---

## 📝 License

Distributed under proprietary license. All rights reserved.
