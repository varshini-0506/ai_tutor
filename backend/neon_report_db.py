import psycopg2
import psycopg2.extras
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NeonReportDatabase:
    def __init__(self, connection_string: str = None):
        """
        Initialize Neon DB connection
        connection_string: Neon DB connection string
        """
        self.connection_string = connection_string or os.getenv('DATABASE_URL')
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable or connection_string is required")
    
    def get_connection(self):
        """Get a database connection"""
        return psycopg2.connect(self.connection_string)
    
    def init_database(self):
        """Initialize the database with the reports table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create the reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id SERIAL PRIMARY KEY,
                    student_name VARCHAR(255) NOT NULL,
                    student_id VARCHAR(100),
                    teacher_id VARCHAR(100),
                    report_data JSONB NOT NULL,
                    pdf_path VARCHAR(500),
                    subject_scores JSONB,
                    topic_completion JSONB,
                    activity_data JSONB,
                    remarks TEXT,
                    report_type VARCHAR(50) DEFAULT 'progress',
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP WITH TIME ZONE
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_student_name ON reports(student_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)')
            
            # Create trigger for updated_at
            cursor.execute('''
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql'
            ''')
            
            cursor.execute('''
                DROP TRIGGER IF EXISTS update_reports_updated_at ON reports;
                CREATE TRIGGER update_reports_updated_at 
                    BEFORE UPDATE ON reports 
                    FOR EACH ROW 
                    EXECUTE FUNCTION update_updated_at_column()
            ''')
            
            conn.commit()
            print("Database initialized successfully")
            
        except Exception as e:
            conn.rollback()
            print(f"Error initializing database: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def save_report(self, student_name: str, report_data: Dict, pdf_path: str = None, 
                   subject_scores: Dict = None, topic_completion: Dict = None, 
                   activity_data: Dict = None, student_id: str = None, 
                   teacher_id: str = None, report_type: str = 'progress') -> int:
        """Save a report to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO reports (
                    student_name, student_id, teacher_id, report_data, pdf_path, 
                    subject_scores, topic_completion, activity_data, report_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                student_name, student_id, teacher_id, 
                json.dumps(report_data), pdf_path,
                json.dumps(subject_scores) if subject_scores else None,
                json.dumps(topic_completion) if topic_completion else None,
                json.dumps(activity_data) if activity_data else None,
                report_type
            ))
            
            report_id = cursor.fetchone()[0]
            conn.commit()
            return report_id
            
        except Exception as e:
            conn.rollback()
            print(f"Error saving report: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_reports_by_student(self, student_name: str, status: str = 'active') -> List[Dict]:
        """Get all reports for a specific student"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cursor.execute('''
                SELECT id, student_name, student_id, teacher_id, report_data, 
                       pdf_path, subject_scores, topic_completion, activity_data, 
                       remarks, report_type, status, created_at, updated_at, 
                       generated_at, expires_at
                FROM reports 
                WHERE student_name = %s AND status = %s
                ORDER BY created_at DESC
            ''', (student_name, status))
            
            reports = cursor.fetchall()
            return [dict(report) for report in reports]
            
        except Exception as e:
            print(f"Error getting reports by student: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_all_reports(self, status: str = 'active', limit: int = None) -> List[Dict]:
        """Get all reports from the database"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            query = '''
                SELECT id, student_name, student_id, teacher_id, report_data, 
                       pdf_path, subject_scores, topic_completion, activity_data, 
                       remarks, report_type, status, created_at, updated_at, 
                       generated_at, expires_at
                FROM reports 
                WHERE status = %s
                ORDER BY created_at DESC
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query, (status,))
            reports = cursor.fetchall()
            return [dict(report) for report in reports]
            
        except Exception as e:
            print(f"Error getting all reports: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_report_by_id(self, report_id: int) -> Optional[Dict]:
        """Get a specific report by ID"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cursor.execute('''
                SELECT id, student_name, student_id, teacher_id, report_data, 
                       pdf_path, subject_scores, topic_completion, activity_data, 
                       remarks, report_type, status, created_at, updated_at, 
                       generated_at, expires_at
                FROM reports 
                WHERE id = %s
            ''', (report_id,))
            
            report = cursor.fetchone()
            return dict(report) if report else None
            
        except Exception as e:
            print(f"Error getting report by ID: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_report(self, report_id: int, **kwargs) -> bool:
        """Update a report with new data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Build dynamic update query
            update_fields = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['report_data', 'subject_scores', 'topic_completion', 'activity_data']:
                    update_fields.append(f"{key} = %s")
                    values.append(json.dumps(value) if value else None)
                else:
                    update_fields.append(f"{key} = %s")
                    values.append(value)
            
            if not update_fields:
                return False
            
            values.append(report_id)
            query = f"UPDATE reports SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor.execute(query, values)
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            print(f"Error updating report: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def add_remark(self, report_id: int, remark: str, teacher_id: str = None) -> bool:
        """Add or update a remark for a specific report"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE reports
                SET remarks = %s, teacher_id = COALESCE(%s, teacher_id)
                WHERE id = %s
            ''', (remark, teacher_id, report_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            print(f"Error adding remark: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def delete_report(self, report_id: int, soft_delete: bool = True) -> bool:
        """Delete a report (soft delete by default)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if soft_delete:
                cursor.execute('UPDATE reports SET status = %s WHERE id = %s', ('deleted', report_id))
            else:
                cursor.execute('DELETE FROM reports WHERE id = %s', (report_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            print(f"Error deleting report: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def search_reports(self, search_term: str, status: str = 'active') -> List[Dict]:
        """Search reports by student name or remarks"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cursor.execute('''
                SELECT id, student_name, student_id, teacher_id, report_data, 
                       pdf_path, subject_scores, topic_completion, activity_data, 
                       remarks, report_type, status, created_at, updated_at, 
                       generated_at, expires_at
                FROM reports 
                WHERE status = %s AND (
                    student_name ILIKE %s OR 
                    remarks ILIKE %s
                )
                ORDER BY created_at DESC
            ''', (status, f'%{search_term}%', f'%{search_term}%'))
            
            reports = cursor.fetchall()
            return [dict(report) for report in reports]
            
        except Exception as e:
            print(f"Error searching reports: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_reports_by_teacher(self, teacher_id: str, status: str = 'active') -> List[Dict]:
        """Get all reports that a teacher has added remarks to"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cursor.execute('''
                SELECT id, student_name, student_id, teacher_id, report_data, 
                       pdf_path, subject_scores, topic_completion, activity_data, 
                       remarks, report_type, status, created_at, updated_at, 
                       generated_at, expires_at
                FROM reports 
                WHERE teacher_id = %s AND status = %s
                ORDER BY created_at DESC
            ''', (teacher_id, status))
            
            reports = cursor.fetchall()
            return [dict(report) for report in reports]
            
        except Exception as e:
            print(f"Error getting reports by teacher: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_report_statistics(self) -> Dict[str, Any]:
        """Get statistics about reports"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_reports,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_reports,
                    COUNT(CASE WHEN remarks IS NOT NULL THEN 1 END) as reports_with_remarks,
                    COUNT(DISTINCT student_name) as unique_students,
                    COUNT(DISTINCT teacher_id) as unique_teachers
                FROM reports
            ''')
            
            stats = cursor.fetchone()
            return {
                'total_reports': stats[0],
                'active_reports': stats[1],
                'reports_with_remarks': stats[2],
                'unique_students': stats[3],
                'unique_teachers': stats[4]
            }
            
        except Exception as e:
            print(f"Error getting report statistics: {e}")
            raise
        finally:
            cursor.close()
            conn.close() 