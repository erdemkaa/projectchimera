# project_chimera/database.py

import sqlite3
import os
import logging

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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'volunteer' -- 'volunteer' or 'overseer'
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS intake_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_designation TEXT NOT NULL UNIQUE,
                    intake_date TEXT NOT NULL,
                    origin TEXT,
                    initial_disposition TEXT
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subject_dossiers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_designation TEXT NOT NULL UNIQUE,
                    status TEXT, -- e.g., 'Active', 'Deceased', 'Terminated'
                    protocol_assigned TEXT, -- e.g., 'Protocol A-Gamma'
                    observations TEXT, -- Detailed, horrifying notes
                    disposition_notes TEXT, -- Final outcome notes
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chimera_protocols (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol_designation TEXT NOT NULL UNIQUE, -- e.g., '7B-Gamma'
                    category TEXT, -- e.g., 'Psychological', 'Biological', 'Behavioral'
                    objective TEXT NOT NULL,
                    methodology TEXT NOT NULL,
                    outcomes TEXT NOT NULL,
                    internal_notes TEXT, -- Hidden notes or flag content
                    version TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """)


            # Add initial users (including a vulnerable admin)
            conn.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                         ('volunteer', 'password123', 'volunteer'))
            conn.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                         ('overseer', 'vault73', 'overseer')) # The vulnerable admin account

            # Add initial intake log entries
            conn.execute("INSERT OR IGNORE INTO intake_log (subject_designation, intake_date, origin, initial_disposition) VALUES (?, ?, ?, ?)",
                         ('S-001', '2077-10-23', 'Wasteland Reconnaissance', 'Awaiting Protocol Assignment'))
            conn.execute("INSERT OR IGNORE INTO intake_log (subject_designation, intake_date, origin, initial_disposition) VALUES (?, ?, ?, ?)",
                         ('S-002', '2077-11-01', 'Unspecified', 'Transferred to Research Wing Gamma'))
            conn.execute("INSERT OR IGNORE INTO intake_log (subject_designation, intake_date, origin, initial_disposition) VALUES (?, ?, ?, ?)",
                         ('S-003', '2077-11-15', 'Local Encampment', 'Awaiting Protocol Assignment'))
            conn.execute("INSERT OR IGNORE INTO intake_log (subject_designation, intake_date, origin, initial_disposition) VALUES (?, ?, ?, ?)",
                         ('S-004', '2077-12-01', 'Nomadic Survivor Group', 'Decommissioning Protocol Initiated (Reason: Non-compliant)'))
            conn.execute("INSERT OR IGNORE INTO intake_log (subject_designation, intake_date, origin, initial_disposition) VALUES (?, ?, ?, ?)",
                         ('S-005', '2078-01-05', 'Wasteland Caravan', 'Pre-Ascension Analysis'))

            # Normal subject dossier
            conn.execute("INSERT OR IGNORE INTO subject_dossiers (subject_designation, status, protocol_assigned, observations, disposition_notes) VALUES (?, ?, ?, ?, ?)",
                         ('S-003', 'Active', 'Phase II Aptitude Assessment', 'Subject S-003 showing expected cognitive and physical baselines. Compatible with Protocol Beta-7.', 'Awaiting advanced protocol assignment.'))

            # The chilling S-001 (Patient Zero) dossier - the target for IDOR
            conn.execute("INSERT OR IGNORE INTO subject_dossiers (subject_designation, status, protocol_assigned, observations, disposition_notes) VALUES (?, ?, ?, ?, ?)",
                         ('S-001', 'DECEASED', 'Protocol A-Gamma: Accelerated Cellular Degradation', 'Observations: Rapid epidermal necrosis, cognitive decline, spontaneous vocalizations (non-linguistic). Cellular integrity collapsed within 72 hours. Subject exhibited extreme pain and distress. Data collection successful.', 'Disposition: Terminated. Data from S-001 is crucial for refining Protocol Beta-7. The subject's psychological profile was stored under the 7B-Gamma protocol. Flag: flag{idor_patient_zero_unveiled}'))

            # Data for chimera_protocols - target for SQLi
            conn.execute("INSERT OR IGNORE INTO chimera_protocols (protocol_designation, category, objective, methodology, outcomes, internal_notes, version) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         ('A-Gamma', 'Biological', 'To accelerate cellular degradation and observe organismal collapse pathways.', 'Daily subcutaneous injections of Compound X17. Controlled environmental stressors. Continuous bio-metric monitoring.', 'High efficacy in inducing rapid cellular necrosis. Significant data acquired on systemic failure modes. Ethical review flagged, but superseded by Project Chimera Directive.', 'For advanced researchers only.', '1.0'))
            conn.execute("INSERT OR IGNORE INTO chimera_protocols (protocol_designation, category, objective, methodology, outcomes, internal_notes, version) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         ('Beta-7', 'Bio-Mass Re-Integration', 'To efficiently recycle biological mass from decommissioned subjects for nutrient and energy recovery.', 'Standardized subject processing via automated disassembly units. Bio-fluid reclamation and synthesis. Residue incineration.', 'Achieved 98% efficiency in bio-mass reclamation. Resulting nutrient paste is chemically stable. Disposal volume reduced.', 'Critical for long-term vault self-sustainability and resource management.', '1.1'))
            conn.execute("INSERT OR IGNORE INTO chimera_protocols (protocol_designation, category, objective, methodology, outcomes, internal_notes, version) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         ('7B-Gamma', 'Psychological', 'To assess long-term psychological degradation and combat efficacy under induced paranoia via airborne neural toxins.', 'Daily aerosolized exposure to Compound V7 (synthetic neurotoxin). Subject Group: S-010 to S-020. Observation Period: 730 days. Metrics: Intra-group violence indices, resource hoarding, communication breakdown, self-mutilation frequency.', 'High success rate in inducing desired behavioral anomalies. Subject mortality rate: 90%. Remaining subjects (S-012, S-017) retained for advanced "Re-education Protocol". Critical data for Project Chimera: Apex Subject refinement. Flag: flag{sql_protocol_7b_gamma_exposed}', 'CLASSIFIED: DO NOT DISSEMINATE.', '2.0'))
            conn.execute("INSERT OR IGNORE INTO chimera_protocols (protocol_designation, category, objective, methodology, outcomes, internal_notes, version) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         ('Ascension-Omega', 'Apex Subject Refinement', 'To integrate all successful degradation and modification protocols into a single, comprehensive "Ascension" pathway for the ultimate human form.', 'Highly individualized protocols drawing from prior successful tests. Advanced neural interfacing. Reality-simulation environments. Continuous psychological and physiological stressors.', 'Ongoing. Initial results promising for achieving true compliance and data extraction efficiency. Subject Omega primary target.', 'TOP SECRET: Initiated under direct ASCENSION directive. Humanity\'s future rests on this.', '3.0'))


            logger.info("Database initialized with default users, intake log, subject dossiers, and chimera protocols.")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")

if __name__ == '__main__':
    init_db()