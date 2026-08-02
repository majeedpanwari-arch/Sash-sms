# 🚀 Sash SMS — Complete Deployment Guide

This guide covers two deployment options for **Sash SMS (Sash SMS Panel)**:

1. **[OPTION A] Instant Free Deployment on Vercel** *(For testing right now with a free `.vercel.app` domain)*
2. **[OPTION B] Hostinger VPS Deployment** *(For your own custom domain & hosting later)*

---

## ⚡ OPTION A: Deploy Free on Vercel (Instant Test)

You can deploy Sash SMS to **Vercel** right now for **FREE** with a live URL (e.g., `https://your-panel.vercel.app`).

### Prerequisites:
- A free account on [Vercel.com](https://vercel.com)
- GitHub account (or Vercel CLI)

---

### Step 1: Push Code to GitHub
1. Create a new repository on GitHub named `abyss-sms-panel`.
2. Push your project folder to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Deploy Sash SMS Panel"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/abyss-sms-panel.git
   git push -u origin main
   ```

---

### Step 2: Import into Vercel
1. Log into your **[Vercel Dashboard](https://vercel.com/dashboard)**.
2. Click **"Add New..."** ➔ **"Project"**.
3. Select your `abyss-sms-panel` repository.
4. Framework Preset: **Other** (Vercel automatically detects `vercel.json` and `@vercel/python`).
5. Expand **Environment Variables** and add:
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = `your_secure_random_key_987654`
6. Click **Deploy**.

🎉 **Done!** Your panel is now live on Vercel at `https://abyss-sms-panel.vercel.app`.

---

## 🌐 OPTION B: Deploy on Hostinger VPS (Custom Domain)

When you buy your Hostinger VPS and custom domain later, follow these steps for production deployment.

### Prerequisites:
1. **Hostinger VPS** (Ubuntu 22.04 LTS recommended).
2. **Custom Domain** (e.g. `yourdomain.com`).

---

### Step 1: Point Domain DNS to Hostinger VPS
1. Log into your Hostinger / Domain Registrar control panel.
2. Go to **DNS Zone Manager**.
3. Add/Update **A Records**:
   - `Name`: `@` ➔ `Points to`: `YOUR_HOSTINGER_VPS_IP`
   - `Name`: `www` ➔ `Points to`: `YOUR_HOSTINGER_VPS_IP`

---

### Step 2: Connect via SSH & Run Deployment Script
1. Connect to your VPS via Terminal / PuTTY:
   ```bash
   ssh root@YOUR_HOSTINGER_VPS_IP
   ```
2. Clone your repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/abyss-sms-panel.git /var/www/abyss_sms
   cd /var/www/abyss_sms
   ```
3. Run the automated installer:
   ```bash
   chmod +x deploy_hostinger.sh
   ./deploy_hostinger.sh
   ```

---

### Step 3: Configure Nginx & Free Let's Encrypt SSL
1. Edit the Nginx template with your domain name:
   ```bash
   sudo cp nginx.conf.template /etc/nginx/sites-available/abyss_sms
   sudo nano /etc/nginx/sites-available/abyss_sms
   ```
   *Replace `YOUR_DOMAIN_HERE` with your domain (e.g., `yourdomain.com`).*

2. Enable the site and restart Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/abyss_sms /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

3. Generate free SSL Certificate:
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

🎉 **Congratulations!** Your Sash SMS Panel is now live on `https://yourdomain.com` with HTTPS SSL!

---

## 🔑 Default Credentials & Panel Usage

### 1. Default Admin Credentials:
- **Username**: `admin`
- **Password**: `admin123`
- *(Important: Change password immediately upon first login in Profile Settings)*

### 2. Admin Capabilities:
- Create new **Agents** and **Clients** (`/admin/admin/add-numbers-to-client`).
- Create and assign SMS ranges & numbers pool.
- Manage pricing tiers (**Rings**) and access code generation (`/verify`).
- Configure auto-delete message timers per client.
- View all real-time incoming SMS messages and system activity logs.

### 3. Client Capabilities:
- View assigned numbers and inbox messages in real-time.
- Query API endpoints with their unique API Token.
