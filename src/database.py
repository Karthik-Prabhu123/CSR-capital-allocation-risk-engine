import sqlite3
import os

# Force absolute path alignment
BASE_DIR = os.getcwd()
DB_DIR = os.path.join(BASE_DIR, "data")
DB_NAME = os.path.join(DB_DIR, "capital_allocation.db")

def get_db_connection():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proposals (
            entity_id TEXT PRIMARY KEY,
            project_name TEXT,
            thematic_area TEXT,
            requested_funding_inr REAL,
            track_record_years INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS risk_metrics (
            entity_id TEXT PRIMARY KEY,
            environmental_score REAL,
            social_efficacy_score REAL,
            governance_risk_rating REAL,
            cost_per_beneficiary REAL,
            FOREIGN KEY (entity_id) REFERENCES proposals(entity_id)
        )
    ''')
    conn.commit()
    conn.close()
    print("✨ Relational schema initialized.")

if __name__ == "__main__":
    init_db()