#!/bin/bash
# Manual requirements installation for cPanel
# Run this via SSH if cPanel auto-install failed

# REPLACE 'username' with your actual cPanel username
USERNAME="username"
VENV_PATH="/home/$USERNAME/virtualenv/api.errandserver.fagitone.com/3.11/bin/activate"
APP_PATH="/home/$USERNAME/api.errandserver.fagitone.com"

echo "Activating virtual environment..."
source $VENV_PATH

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
cd $APP_PATH
pip install -r requirements.txt

echo "Verifying installations..."
pip list | grep -E "Django|psycopg2|djangorestframework"

echo "Done! Now restart your Python app in cPanel."
