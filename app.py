# project_chimera/app.py

import json
import base64
from functools import wraps
import os
from urllib import request as url_request
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, g, flash, make_response
from config import Config
from database import init_db, get_db_connection
import logging
import hashlib
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = 'instance/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None or g.user['role'] != 'admin':
            flash("Access Denied. Administrator privileges required.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

with app.app_context():
    init_db()

@app.before_request
def load_logged_in_user():
    session_cookie = request.cookies.get('vault_session_data')
    g.user = None
    if session_cookie:
        try:
            decoded_data = base64.b64decode(session_cookie).decode('utf-8')
            session_data = json.loads(decoded_data)
            # Trust the data in the cookie entirely
            g.user = session_data
        except (json.JSONDecodeError, base64.binascii.Error, UnicodeDecodeError):
            # Invalid cookie, treat as logged out
            g.user = None

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    if not g.user:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    posts = conn.execute('''
        SELECT p.content, p.timestamp, u.username, u.profile_picture, u.id as user_id
        FROM posts p JOIN users u ON p.user_id = u.id
        ORDER BY p.timestamp DESC
    ''').fetchall()
    conn.close()
    return render_template('feed.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('index'))

    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password)).fetchone()
        conn.close()

        if user is None:
            error = "Invalid credentials. Please try again."
            logger.warning(f"Failed login attempt for username: {username}")
        else:
            # Create a dictionary with user data
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
            # Base64 encode the JSON string
            encoded_data = base64.b64encode(json.dumps(user_data).encode('utf-8')).decode('utf-8')
            
            response = make_response(redirect(url_for('index')))
            response.set_cookie('vault_session_data', encoded_data)
            logger.info(f"User {user['username']} ({user['role']}) logged in successfully.")
            return response

    flash(error)
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.set_cookie('vault_session_data', '', expires=0)
    flash("You have been logged out.")
    return response

@app.route('/profile/<int:user_id>')
def profile(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    posts = conn.execute('SELECT * FROM posts WHERE user_id = ? ORDER BY timestamp DESC', (user_id,)).fetchall()

    # Fetch comments for each post on profile page
    posts_with_comments = []
    for post in posts:
        post_dict = dict(post)
        comments = conn.execute('''
            SELECT c.content, c.timestamp, u.username, u.profile_picture
            FROM comments c JOIN users u ON c.user_id = u.id
            WHERE c.post_id = ?
            ORDER BY c.timestamp ASC
        ''', (post['id'],)).fetchall()
        post_dict['comments'] = comments
        posts_with_comments.append(post_dict)

    conn.close()

    if user is None:
        flash("User not found.")
        return redirect(url_for('index'))

    # The g.user is now a dict, so we pass the user object from the db separately
    return render_template('profile.html', user=user, posts=posts_with_comments, current_user=g.user)

@app.route('/create_post', methods=['POST'])
def create_post():
    if not g.user:
        flash("You must be logged in to post.")
        return redirect(url_for('login'))

    content = request.form['content']
    if content:
        conn = get_db_connection()
        conn.execute('INSERT INTO posts (user_id, content) VALUES (?, ?)', (g.user['id'], content))
        conn.commit()
        conn.close()
        flash("Post created successfully!")
    else:
        flash("Post content cannot be empty.")
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('query', '')
    query_results = []
    if query:
        conn = get_db_connection()
        # SQL Injection Vulnerability: Direct concatenation of user input
        sql_query = f"SELECT id, username, bio, profile_picture FROM users WHERE username LIKE '%{query}%' OR bio LIKE '%{query}%'"
        try:
            query_results = conn.execute(sql_query).fetchall()
        except Exception as e:
            flash(f"Search error: {e}")
            logger.error(f"SQL Injection attempt detected: {sql_query}")
        finally:
            conn.close()

    return render_template('search.html', query_results=query_results)

@app.route('/edit_bio', methods=['POST'])
def edit_bio():
    if not g.user:
        flash("You must be logged in to edit your bio.")
        return redirect(url_for('login'))

    new_bio = request.form['bio']
    conn = get_db_connection()
    # Stored XSS Vulnerability: No sanitization of bio content
    conn.execute('UPDATE users SET bio = ? WHERE id = ?', (new_bio, g.user['id']))
    conn.commit()
    conn.close()
    flash("Bio updated successfully!")
    return redirect(url_for('profile', user_id=g.user['id']))

@app.route('/admin_data_sync', methods=['GET', 'POST'])
@admin_required
def admin_data_sync():
    sync_result = None
    error = None
    if request.method == 'POST':
        if 'report_file' in request.files and request.files['report_file'].filename != '':
            file = request.files['report_file']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            file_size = os.path.getsize(filepath)
            sync_result = f"Report '{filename}' uploaded successfully. Size: {file_size} bytes."
            # Clean up the uploaded file
            os.remove(filepath)
        elif 'remote_url' in request.form and request.form['remote_url'] != '':
            remote_url = request.form['remote_url']
            try:
                with url_request.urlopen(remote_url, timeout=5) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    sync_result = f"Successfully fetched content from {remote_url}:

{content[:200]}..."
            except Exception as e:
                error = f"Error fetching data from URL: {e}"
        else:
            error = "Please select a file or provide a URL."

    return render_template('admin_data_sync.html', sync_result=sync_result, error=error)

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

if __name__ == '__main__':
    logger.info(f"Application starting in directory: {os.getcwd()}")
    app.run(host='0.0.0.0', port=5000, debug=False)
