# project_chimera/config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_should_be_replaced_in_production'
    # Define database path relative to the script's location
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'vault73.db')

    # You might consider adding flags as config variables in a real CTF,
    # but for simplicity, they are embedded in the database or files for now.