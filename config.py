# project_chimera/config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_for_vault_connect'
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'vault_connect.db')
    ADMIN_PANEL_URL = '/admin_control_panel_ax73' # This is the XSS flag
