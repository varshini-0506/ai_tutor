import sqlite3
import os
from datetime import datetime

class ReportDatabase:
    def __init__(self, db_path='reports.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the reports table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add 'remarks' column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE reports ADD COLUMN remarks TEXT')
            conn.commit()
            print("Added 'remarks' column to reports table.")
        except sqlite3.OperationalError:
            # Column already exists
            pass

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                report_data TEXT NOT NULL,
                pdf_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subject_scores TEXT,
                topic_completion TEXT,
                activity_data TEXT,
                remarks TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_report(self, student_name, report_data, pdf_path, subject_scores=None, topic_completion=None, activity_data=None):
        """Save a report to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reports (student_name, report_data, pdf_path, subject_scores, topic_completion, activity_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (student_name, report_data, pdf_path, subject_scores, topic_completion, activity_data))
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return report_id
    
    def get_reports_by_student(self, student_name):
        """Get all reports for a specific student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, student_name, report_data, pdf_path, created_at, subject_scores, topic_completion, activity_data, remarks
            FROM reports 
            WHERE student_name = ?
            ORDER BY created_at DESC
        ''', (student_name,))
        
        reports = cursor.fetchall()
        conn.close()
        
        return reports
    
    def get_all_reports(self):
        """Get all reports from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, student_name, report_data, pdf_path, created_at, subject_scores, topic_completion, activity_data, remarks
            FROM reports 
            ORDER BY created_at DESC
        ''')
        
        reports = cursor.fetchall()
        conn.close()
        
        return reports
    
    def get_report_by_id(self, report_id):
        """Get a specific report by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, student_name, report_data, pdf_path, created_at, subject_scores, topic_completion, activity_data, remarks
            FROM reports 
            WHERE id = ?
        ''', (report_id,))
        
        report = cursor.fetchone()
        conn.close()
        
        return report
    
    def delete_report(self, report_id):
        """Delete a report from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM reports WHERE id = ?', (report_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def add_remark(self, report_id, remark):
        """Add or update a remark for a specific report."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reports
            SET remarks = ?
            WHERE id = ?
        ''', (remark, report_id))
        
        conn.commit()
        conn.close()
        
        return True 