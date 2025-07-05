# project_chimera/database.py

import sqlite3
import os
import logging
import hashlib # For password hashing

# Configure logging for database operations
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use the Config to get the database path
from config import Config
DATABASE_PATH = Config.DATABASE

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # This allows access to columns by name
    return conn

def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("DROP TABLE IF EXISTS comments;")
            conn.execute("DROP TABLE IF EXISTS posts;")
            conn.execute("DROP TABLE IF EXISTS users;")

            conn.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user', -- 'user', 'admin', 'subject'
                    bio TEXT DEFAULT '',
                    profile_picture TEXT DEFAULT 'default.png'
                );
            """)
            conn.execute("""
                CREATE TABLE posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
            """)
            conn.execute("""
                CREATE TABLE comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES posts (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
            """)

            # --- Initial Data ---

            # User for bruteforce (password: password)
            conn.execute("INSERT INTO users (username, password, role, bio, profile_picture) VALUES (?, ?, ?, ?, ?)",
                         ('overseer', 'e10adc3949ba59abbe56e057f20f883e', 'The one in charge.', 'overseer.png', 'user'),  # Password is '123456')

            # Admin user (for SQLi target)
            conn.execute("INSERT INTO users (username, password, role, bio, profile_picture) VALUES (?, ?, ?, ?, ?)",
                         ('Dr_Albright', hashlib.md5(b'secure_admin_pass').hexdigest(), 'admin', 'Lead researcher for Project Chimera. Compliance is key.', 'Dr_Albright.png'))

            # Hidden Subject S-001 (for IDOR)
            conn.execute("INSERT INTO users (id, username, password, role, bio, profile_picture) VALUES (?, ?, ?, ?, ?, ?)",
                         (73, 'Subject_S001', hashlib.md5(b'redacted').hexdigest(), 'subject', '[REDACTED] Initial observations: Subject exhibits extreme cellular degradation and cognitive regression. Vocalizations are non-linguistic, indicative of profound distress. Data from this subject is critical for understanding the limits of the Apex Consciousness cultivation. Further details are logged in the Project Chimera Operations Log. Flag: flag{idor_vault_subject_uncovered}', 'subject_s001.png'))

            # Other regular users
            conn.execute("INSERT INTO users (username, password, role, bio, profile_picture) VALUES (?, ?, ?, ?, ?)",
                         ('VaultDweller42', hashlib.md5(b'vaultlife').hexdigest(), 'user', 'Living the dream in Vault 73!', 'vaultdweller42.png'))
            conn.execute("INSERT INTO users (username, password, role, bio, profile_picture) VALUES (?, ?, ?, ?, ?)",
                         ('RadScorpionFan', hashlib.md5(b'wasteland').hexdigest(), 'user', 'Love exploring the irradiated wastes. Any tips for finding Nuka-Cola?', 'radscorpionfan.png'))

            # New paranoid user
            conn.execute("INSERT INTO users (username, password, role, bio) VALUES (?, ?, ?, ?)",
                         ('Whisperer73', hashlib.md5(b'eyes_everywhere').hexdigest(), 'user', "They're always watching. Always listening. Don't trust the silence."))

            # Initial Posts
            conn.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)",
                         (1, 'Just another day overseeing the future of humanity. Stay vigilant, Vault-Dwellers!'))
            conn.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)",
                         (3, 'Anyone else excited for the next G.O.A.T. exams? #VaultLife'))
            conn.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)",
                         (4, 'Found some interesting flora near Sector 7. Might be edible? #SurvivalTips'))
            conn.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)",
                         (2, 'Reminder: All research data must be logged and cross-referenced. Deviations will not be tolerated.'))

            # Posts from Whisperer73
            conn.execute("INSERT INTO posts (user_id, content) VALUES ((SELECT id FROM users WHERE username = 'Whisperer73'), ?)",
                         ('The walls have ears. The screens have eyes. Be careful what you share. #VaultSecrets',))
            conn.execute("INSERT INTO posts (user_id, content) VALUES ((SELECT id FROM users WHERE username = 'Whisperer73'), ?)",
                         ('Heard strange noises from Sector 5 last night. They say it''s just maintenance. I don''t believe them. #SomethingIsWrong',))
            conn.execute("INSERT INTO posts (user_id, content) VALUES ((SELECT id FROM users WHERE username = 'Whisperer73'), ?)",
                         ('Why do they always ask about our dreams? What are they looking for? #Vault73',))

            # Comments on Whisperer73's posts
            conn.execute("""INSERT INTO comments (post_id, user_id, content) VALUES (
                (SELECT id FROM posts WHERE content LIKE '%The walls have ears%'),
                (SELECT id FROM users WHERE username = 'VaultDweller42'),
                'Relax, Whisperer. It''s just the ventilation system. You''re safe here.'
            )""")
            conn.execute("""INSERT INTO comments (post_id, user_id, content) VALUES (
                (SELECT id FROM posts WHERE content LIKE '%Heard strange noises%'),
                (SELECT id FROM users WHERE username = 'Dr_Albright'),
                'Whisperer73: All systems are nominal. Any perceived anomalies are a result of routine maintenance. Please refrain from spreading misinformation.'
            )""")
            conn.execute("""INSERT INTO comments (post_id, user_id, content) VALUES (
                (SELECT id FROM posts WHERE content LIKE '%Why do they always ask about our dreams%'),
                (SELECT id FROM users WHERE username = 'RadScorpionFan'),
                'It''s for our psychological well-being, obviously. Don''t you want to be well-adjusted?'
            )""")

            logger.info("Database initialized for Vault-Connect.")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")

if __name__ == '__main__':
    init_db()
