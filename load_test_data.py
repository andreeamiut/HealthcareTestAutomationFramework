#!/usr/bin/env python3
"""
Load test data into the healthcare database.

This module provides functionality to load sample patient and appointment data
into the SQLite healthcare database for testing purposes.
"""

import sqlite3
import json
from datetime import datetime

def load_test_data():
    """
    Load test data into the healthcare database.

    This function connects to the SQLite database 'data/healthcare.db',
    loads sample patient and appointment data from JSON files,
    adds timestamps, and inserts the data into the respective tables.
    """
    # Connect to database
    with sqlite3.connect('data/healthcare.db') as conn:
        cursor = conn.cursor()

        # Load patients
        with open('data/test_data/sample_patients.json', 'r', encoding='utf-8') as f:
            patients = json.load(f)

        for patient in patients:
            # Add timestamps
            patient['created_date'] = datetime.now().isoformat()
            patient['updated_date'] = datetime.now().isoformat()
            patient['created_by'] = 'TEST_SETUP'

            columns = list(patient.keys())
            placeholders = ['?' for _ in columns]
            values = list(patient.values())

            insert_sql = f"""
            INSERT OR REPLACE INTO patients ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            """

            cursor.execute(insert_sql, values)

        # Load appointments
        with open('data/test_data/sample_appointments.json', 'r', encoding='utf-8') as f:
            appointments = json.load(f)

        for appointment in appointments:
            # Add timestamps
            appointment['created_date'] = datetime.now().isoformat()
            appointment['updated_date'] = datetime.now().isoformat()

            columns = list(appointment.keys())
            placeholders = ['?' for _ in columns]
            values = list(appointment.values())

            insert_sql = f"""
            INSERT OR REPLACE INTO appointments ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            """

            cursor.execute(insert_sql, values)

    print('Test data loaded successfully')

if __name__ == "__main__":
    load_test_data()
