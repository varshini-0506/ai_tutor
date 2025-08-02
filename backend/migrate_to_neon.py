#!/usr/bin/env python3
"""
Migration script to set up Neon DB for the AI Tutor application
This script helps migrate from SQLite to Neon DB and sets up the new schema
"""

import os
import sys
import json
from datetime import datetime
from neon_report_db import NeonReportDatabase
from config import Config

def setup_environment():
    """Set up environment variables"""
    print("🔧 Setting up environment...")
    
    # Check if DATABASE_URL is set
    if not Config.get_database_url():
        print("❌ Error: DATABASE_URL or NEON_DB_URL environment variable not set")
        print("Please set your Neon DB connection string as an environment variable:")
        print("export DATABASE_URL='postgresql://username:password@host:port/database'")
        print("or")
        print("export NEON_DB_URL='postgresql://username:password@host:port/database'")
        return False
    
    print("✅ Database URL configured")
    return True

def initialize_database():
    """Initialize the Neon DB with the reports table"""
    print("🗄️ Initializing database...")
    
    try:
        db = NeonReportDatabase()
        db.init_database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def migrate_existing_data():
    """Migrate existing data from SQLite to Neon DB (if applicable)"""
    print("🔄 Checking for existing SQLite data...")
    
    sqlite_db_path = 'reports.db'
    if not os.path.exists(sqlite_db_path):
        print("ℹ️ No existing SQLite database found, skipping migration")
        return True
    
    try:
        import sqlite3
        conn = sqlite3.connect(sqlite_db_path)
        cursor = conn.cursor()
        
        # Get existing reports
        cursor.execute('SELECT * FROM reports')
        existing_reports = cursor.fetchall()
        
        if not existing_reports:
            print("ℹ️ No existing reports found in SQLite database")
            return True
        
        print(f"📊 Found {len(existing_reports)} existing reports to migrate")
        
        # Initialize Neon DB
        neon_db = NeonReportDatabase()
        
        migrated_count = 0
        for report in existing_reports:
            try:
                # Parse existing data
                report_id, student_name, report_data, pdf_path, created_at, subject_scores, topic_completion, activity_data, remarks = report
                
                # Convert to new format
                parsed_report_data = json.loads(report_data) if isinstance(report_data, str) else report_data
                parsed_subject_scores = json.loads(subject_scores) if subject_scores else None
                parsed_topic_completion = json.loads(topic_completion) if topic_completion else None
                parsed_activity_data = json.loads(activity_data) if activity_data else None
                
                # Save to Neon DB
                neon_db.save_report(
                    student_name=student_name,
                    report_data=parsed_report_data,
                    pdf_path=pdf_path,
                    subject_scores=parsed_subject_scores,
                    topic_completion=parsed_topic_completion,
                    activity_data=parsed_activity_data
                )
                
                # Add remarks if they exist
                if remarks:
                    # Get the newly created report ID
                    reports = neon_db.get_reports_by_student(student_name)
                    if reports:
                        neon_db.add_remark(reports[0]['id'], remarks)
                
                migrated_count += 1
                print(f"✅ Migrated report for {student_name}")
                
            except Exception as e:
                print(f"❌ Error migrating report for {student_name}: {e}")
        
        print(f"🎉 Successfully migrated {migrated_count} reports")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    print("📝 Creating sample data...")
    
    try:
        db = NeonReportDatabase()
        
        # Sample report data
        sample_reports = [
            {
                'student_name': 'Alice Johnson',
                'report_data': {
                    'student_name': 'Alice Johnson',
                    'total_score': 92,
                    'overall_percentage': 92.5,
                    'subjects': ['Math', 'Science', 'English'],
                    'summary': 'Excellent progress in all subjects with strong analytical skills.',
                    'recommendations': ['Continue advanced math practice', 'Explore science projects']
                },
                'subject_scores': {
                    'Math': 95,
                    'Science': 88,
                    'English': 92,
                    'History': 90
                },
                'topic_completion': {
                    'Math': {'completed': 18, 'total': 20, 'percentage': 90},
                    'Science': {'completed': 20, 'total': 22, 'percentage': 91},
                    'English': {'completed': 16, 'total': 18, 'percentage': 89}
                },
                'activity_data': {
                    'weekly_activity': [
                        {'day': 'Monday', 'activities': 4},
                        {'day': 'Tuesday', 'activities': 6},
                        {'day': 'Wednesday', 'activities': 5},
                        {'day': 'Thursday', 'activities': 7},
                        {'day': 'Friday', 'activities': 3}
                    ],
                    'total_activities': 25,
                    'average_daily': 5.0
                },
                'remarks': 'Alice shows exceptional dedication and consistently high performance. Great analytical thinking skills!'
            },
            {
                'student_name': 'Bob Smith',
                'report_data': {
                    'student_name': 'Bob Smith',
                    'total_score': 78,
                    'overall_percentage': 78.2,
                    'subjects': ['Math', 'Science', 'English'],
                    'summary': 'Good progress with room for improvement in certain areas.',
                    'recommendations': ['Focus on math fundamentals', 'Practice reading comprehension']
                },
                'subject_scores': {
                    'Math': 75,
                    'Science': 80,
                    'English': 72,
                    'History': 85
                },
                'topic_completion': {
                    'Math': {'completed': 12, 'total': 20, 'percentage': 60},
                    'Science': {'completed': 16, 'total': 22, 'percentage': 73},
                    'English': {'completed': 14, 'total': 18, 'percentage': 78}
                },
                'activity_data': {
                    'weekly_activity': [
                        {'day': 'Monday', 'activities': 2},
                        {'day': 'Tuesday', 'activities': 3},
                        {'day': 'Wednesday', 'activities': 4},
                        {'day': 'Thursday', 'activities': 2},
                        {'day': 'Friday', 'activities': 3}
                    ],
                    'total_activities': 14,
                    'average_daily': 2.8
                },
                'remarks': 'Bob is making steady progress. Would benefit from additional practice in math fundamentals.'
            }
        ]
        
        for report in sample_reports:
            db.save_report(
                student_name=report['student_name'],
                report_data=report['report_data'],
                subject_scores=report['subject_scores'],
                topic_completion=report['topic_completion'],
                activity_data=report['activity_data']
            )
            
            # Add remarks
            reports = db.get_reports_by_student(report['student_name'])
            if reports:
                db.add_remark(reports[0]['id'], report['remarks'])
        
        print("✅ Sample data created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def test_database_connection():
    """Test the database connection and basic operations"""
    print("🧪 Testing database connection...")
    
    try:
        db = NeonReportDatabase()
        
        # Test basic operations
        stats = db.get_report_statistics()
        print(f"📊 Database statistics: {stats}")
        
        # Test getting all reports
        reports = db.get_all_reports(limit=5)
        print(f"📋 Found {len(reports)} reports in database")
        
        print("✅ Database connection and operations working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting Neon DB Migration for AI Tutor")
    print("=" * 50)
    
    # Print current configuration
    Config.print_config()
    print()
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Migrate existing data
    if not migrate_existing_data():
        print("⚠️ Migration failed, but continuing...")
    
    # Create sample data (optional)
    create_sample = input("Create sample data for testing? (y/n): ").lower().strip()
    if create_sample == 'y':
        create_sample_data()
    
    # Test database
    if not test_database_connection():
        sys.exit(1)
    
    print("\n🎉 Migration completed successfully!")
    print("You can now use Neon DB with your AI Tutor application.")
    print("\nNext steps:")
    print("1. Update your app.py to use NeonReportDatabase instead of ReportDatabase")
    print("2. Set your DATABASE_URL environment variable")
    print("3. Restart your Flask application")

if __name__ == "__main__":
    main() 