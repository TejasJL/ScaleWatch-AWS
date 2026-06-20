#!/bin/bash
# ScaleWatch EC2 Startup Script
# Runs automatically when new instance launches via Auto Scaling

# Update OS packages
yum update -y

# Install Python 3, pip, and git
yum install -y python3 python3-pip git

# Clone your app from GitHub  ← REPLACE with your actual repo URL
git clone https://github.com/YOUR_USERNAME/scalewatch-aws.git /home/ec2-user/scalewatch

# Install Python dependencies
pip3 install -r /home/ec2-user/scalewatch/requirements.txt

# Fix ownership
chown -R ec2-user:ec2-user /home/ec2-user/scalewatch

# Create systemd service (auto-restart on crash or reboot)
cat > /etc/systemd/system/scalewatch.service << 'EOF'
[Unit]
Description=ScaleWatch Flask Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/scalewatch
ExecStart=/usr/local/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable scalewatch
systemctl start scalewatch

echo "ScaleWatch started successfully" >> /var/log/scalewatch-init.log