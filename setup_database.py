#!/usr/bin/env python3
import sqlite3
import os

def setup_database():
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    # Connect to SQLite database
    conn = sqlite3.connect('data/healthcare.db')
    cursor = conn.cursor()

    # Read and execute schema
    with open('data/sql_scripts/healthcare_schema.sql', 'r') as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()

    print('Database schema created successfully')

if __name__ == "__main__":
    setup_database()