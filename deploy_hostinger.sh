#!/bin/bash
# =========================================================
# ABYSS SMS — Automated 1-Click Hostinger VPS Installer
# =========================================================

set -e

echo "🚀 Starting ABYSS SMS Hostinger VPS Automated Setup..."

# Update package lists
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl

# Set install directory
INSTALL_DIR="/var/www/abyss_sms"

if [ -d "$INSTALL_DIR" ]; then
    echo "📁 Directory $INSTALL_DIR exists. Updating codebase..."
else
    echo "📁 Creating installation directory $INSTALL_DIR..."
    sudo mkdir -p $INSTALL_DIR
    sudo chown -R $USER:$USER $INSTALL_DIR
fi

# Copy codebase
cp -r . $INSTALL_DIR/
cd $INSTALL_DIR

# Create virtual environment
echo "🐍 Setting up Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Setup Systemd Service
echo "⚙️ Configuring Systemd Service..."
sudo cp abyss_sms.service.template /etc/systemd/system/abyss_sms.service
sudo systemctl daemon-reload
sudo systemctl enable abyss_sms
sudo systemctl restart abyss_sms

echo "✅ ABYSS SMS setup complete!"
echo "Next step: Configure Nginx with your domain name and run certbot for free SSL."
