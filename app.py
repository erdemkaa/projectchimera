# project_chimera/app.py

from flask import Flask, render_template, request, redirect, url_for, session, g, flash, abort
from config import Config
from database import init_db, get_db_connection
import logging
import os
import requests # Import requests library for making HTTP requests

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database is initialized when app starts
with app.app_context():
    init_db()

# --- Before/After Request Hooks ---
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        conn = get_db_connection()
        g.user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Routes ---

@app.route('/')
def index():
    if g.user:
        if g.user['role'] == 'overseer':
            return redirect(url_for('overseer_dashboard'))
        else:
            # Volunteer's basic profile
            return render_template('public/index.html', message="Welcome, Volunteer. Your Phase I Aptitude Assessment is pending.")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if user is None:
            error = "Invalid credentials. Please try again, Volunteer."
            logger.warning(f"Failed login attempt for username: {username}")
        else:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            logger.info(f"User {user['username']} ({user['role']}) logged in successfully.")
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out. Until next time, Vault-Dweller.")
    return redirect(url_for('login'))


@app.route('/overseer/dashboard')
def overseer_dashboard():
    if not g.user or g.user['role'] != 'overseer':
        flash("Access Denied. Overseer credentials required.")
        return redirect(url_for('login'))

    message = "Welcome, Overseer. Your Vault Management Dashboard. Proceed with Project Chimera."
    return render_template('overseer/dashboard.html', message=message)

@app.route('/overseer/intake_log_snippets')
def intake_log_snippets():
    if not g.user or g.user['role'] != 'overseer':
        flash("Access Denied. Overseer credentials required.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM intake_log ORDER BY intake_date DESC LIMIT 5').fetchall() # Show only recent for 'snippets'
    conn.close()

    lore_message = "Intake Log Fragment (Ascension Code: A-212-Delta): Glimpse into recent subject dispositions. Data is limited for security protocols."
    return render_template('overseer/intake_log.html', logs=logs, lore_message=lore_message)

@app.route('/overseer/subject_dossier')
def subject_dossier():
    if not g.user or g.user['role'] != 'overseer':
        flash("Access Denied. Overseer credentials required.")
        return redirect(url_for('login'))

    subject_designation = request.args.get('id', 'S-003') # Default to S-003 for 'normal' view
    conn = get_db_connection()
    dossier = conn.execute('SELECT * FROM subject_dossiers WHERE subject_designation = ?', (subject_designation,)).fetchone()
    conn.close()

    if dossier:
        lore_message = f"Subject Dossier: {dossier['subject_designation']}. Accessing designated records. (Restricted Access - View Only)"
        return render_template('overseer/subject_dossier.html', dossier=dossier, lore_message=lore_message)
    else:
        flash(f"Subject Dossier for {subject_designation} not found or inaccessible.")
        return redirect(url_for('overseer_dashboard'))

@app.route('/overseer/psycho_aptitude_scan', methods=['GET', 'POST'])
def psycho_aptitude_scan():
    if not g.user or g.user['role'] != 'overseer':
        flash("Access Denied. Overseer credentials required.")
        return redirect(url_for('login'))

    scan_result = None
    if request.method == 'POST':
        subject_input = request.form.get('subject_designation', '')
        scan_result = f"ERROR: Subject Emotional Feedback Loop Detected. Unforeseen Echo: <span class='xss-output'>{subject_input}</span>"
    elif request.method == 'GET' and 'scan_input' in request.args:
        subject_input = request.args.get('scan_input', '')
        scan_result = f"ERROR: Subject Emotional Feedback Loop Detected. Unforeseen Echo: <span class='xss-output'>{subject_input}</span>"

    lore_message = "This terminal monitors subject emotional states. Input a designation to retrieve the last recorded psycho-aptitude echo. Be advised: system stability is compromised."
    return render_template('overseer/psycho_aptitude_scan.html', lore_message=lore_message, scan_result=scan_result)

@app.route('/overseer/research_query', methods=['GET'])
def research_query():
    if not g.user or g.user['role'] != 'overseer':
        flash("Access Denied. Overseer credentials required.")
        return redirect(url_for('login'))

    category_id = request.args.get('category_id', '1') # Default to '1' for a sample query
    protocol_results = []
    error = None

    conn = get_db_connection()
    try:
        query = f"SELECT protocol_designation, category, objective FROM chimera_protocols WHERE id = {category_id};"
        logger.info(f"Executing SQL Query (vulnerable): {query}")
        protocol_results = conn.execute(query).fetchall()

        if not protocol_results and category_id != '1':
            error = "No protocols found for the specified category ID. Please check your input."
    except sqlite3.Error as e:
        error = f"Database Query Error: {e}. Malformed input detected. Alerting ASCENSION."
        logger.error(f"SQL Injection attempt detected with input '{category_id}': {e}")
    finally:
        conn.close()

    lore_message = "Accessing high-level research protocols. Enter a 'Protocol Category ID' for data overview. (Note: Data access is filtered for security.)"
    return render_template('overseer/research_query.html', lore_message=lore_message, protocols=protocol_results, error=error)

@app.route('/overseer/surveillance_archive')
def surveillance_archive():
    if not g.user or g.user['role'] != 'overseer':
        flash("Access Denied. Overseer credentials required.")
        return redirect(url_for('login'))

    log_filename = request.args.get('log_file', 'access_log_vault73.txt') # Default to a 'safe' log
    log_content = None
    error = None

    base_dir = app.root_path
    target_path = os.path.join(base_dir, log_filename)

    try:
        if os.path.isdir(target_path):
            error = "Access Denied: Cannot view directory contents."
            logger.warning(f"LFI attempt to list directory: {target_path}")
        elif not os.path.exists(target_path):
            error = f"Log file '{log_filename}' not found. Please verify the log designation."
            logger.warning(f"LFI attempt - file not found: {target_path}")
        else:
            with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
            logger.info(f"Successfully read log file: {target_path}")
    except Exception as e:
        error = f"System Error: Unable to retrieve log. Possible data corruption. ({e})"
        logger.error(f"LFI attempt failed or file read error on {target_path}: {e}")

    lore_message = "Reviewing archived surveillance footage logs. Enter a specific log file designation to view its contents. (Note: Most recent logs are automatically purged for storage efficiency.)"
    return render_template('overseer/surveillance_archive.html', lore_message=lore_message, log_content=log_content, error=error, current_log_file=log_filename)


# --- ROUTE FOR STAGE 6: Remote Data Synchronization (SSRF Vulnerability) ---
@app.route('/overseer/remote_sync', methods=['GET', 'POST'])
def remote_sync():
    if not g.user or g.user['role'] != 'overseer':
        flash("Access Denied. Overseer credentials required.")
        return redirect(url_for('login'))

    sync_result = None
    remote_url = ""
    error = None

    if request.method == 'POST':
        remote_url = request.form.get('remote_url', '').strip()
        if not remote_url:
            error = "Please provide a URL for synchronization."
        else:
            try:
                # VULNERABILITY: SSRF - The application makes a request to a user-supplied URL
                # without proper validation, allowing access to internal network resources.
                response = requests.get(remote_url, timeout=5)
                sync_result = f"--- Remote System Response (HTTP Status: {response.status_code}) ---\n"
                sync_result += response.text[:2000] # Limit output to prevent overwhelming the page
                if len(response.text) > 2000:
                    sync_result += "\n... (response truncated)"
                logger.info(f"SSRF request to {remote_url} successful (Status: {response.status_code})")

            except requests.exceptions.Timeout:
                error = "Synchronization timed out. Remote system did not respond."
                logger.warning(f"SSRF request to {remote_url} timed out.")
            except requests.exceptions.ConnectionError:
                error = "Connection failed. Unable to reach remote system. Check URL or network status."
                logger.warning(f"SSRF request to {remote_url} connection error.")
            except requests.exceptions.RequestException as e:
                error = f"An unexpected error occurred during synchronization: {e}"
                logger.error(f"SSRF request to {remote_url} failed with: {e}")

    lore_message = "Initiate secure data synchronization with external Vault-Tec data nodes. Input the remote node's URL to begin the transfer. (Protocols A-7.3.1 enforced.)"
    return render_template('overseer/remote_sync.html', lore_message=lore_message, sync_result=sync_result, error=error, current_url=remote_url)


@app.route('/overseer/ascension_override', methods=['GET', 'POST'])
def ascension_override():
    if not g.user or g.user['role'] != 'overseer':
        flash("Access Denied. Overseer credentials required.")
        return redirect(url_for('login'))

    message = None
    if request.method == 'POST':
        override_code = request.form.get('override_code')
        # The final flag from the SSRF challenge
        if override_code == 'flag{ASCENSION_OVERRIDE_CODE_737351}':
            message = "OVERRIDE ACCEPTED. Project Chimera is terminated. You have saved what remains of their humanity."
        else:
            message = "OVERRIDE REJECTED. Invalid code."

    return render_template('overseer/ascension_override.html', message=message)


# --- Run the App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)