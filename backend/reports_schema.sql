-- Reports Table Schema for Neon DB
-- This table stores all student progress reports with teacher remarks

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    student_name VARCHAR(255) NOT NULL,
    student_id VARCHAR(100), -- Optional: if you have unique student IDs
    teacher_id VARCHAR(100), -- Optional: to track which teacher added remarks
    report_data JSONB NOT NULL, -- Stores the complete report data as JSON
    pdf_path VARCHAR(500), -- Path to the generated PDF file
    subject_scores JSONB, -- Stores subject-wise scores as JSON
    topic_completion JSONB, -- Stores topic completion data as JSON
    activity_data JSONB, -- Stores weekly activity data as JSON
    remarks TEXT, -- Teacher's remarks/feedback
    report_type VARCHAR(50) DEFAULT 'progress', -- Type of report (progress, assessment, etc.)
    status VARCHAR(20) DEFAULT 'active', -- Status: active, archived, deleted
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE -- Optional: for report expiration
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_reports_student_name ON reports(student_name);
CREATE INDEX IF NOT EXISTS idx_reports_student_id ON reports(student_id);
CREATE INDEX IF NOT EXISTS idx_reports_teacher_id ON reports(teacher_id);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_report_type ON reports(report_type);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_reports_student_status ON reports(student_name, status);
CREATE INDEX IF NOT EXISTS idx_reports_teacher_status ON reports(teacher_id, status);

-- Full-text search index for remarks (if using PostgreSQL)
CREATE INDEX IF NOT EXISTS idx_reports_remarks_fts ON reports USING gin(to_tsvector('english', remarks));

-- Trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_reports_updated_at 
    BEFORE UPDATE ON reports 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE reports IS 'Stores all student progress reports with teacher remarks and analytics data';
COMMENT ON COLUMN reports.student_name IS 'Name of the student';
COMMENT ON COLUMN reports.student_id IS 'Unique identifier for the student (optional)';
COMMENT ON COLUMN reports.teacher_id IS 'ID of the teacher who added remarks (optional)';
COMMENT ON COLUMN reports.report_data IS 'Complete report data stored as JSONB for flexibility';
COMMENT ON COLUMN reports.pdf_path IS 'File path to the generated PDF report';
COMMENT ON COLUMN reports.subject_scores IS 'Subject-wise scores stored as JSONB';
COMMENT ON COLUMN reports.topic_completion IS 'Topic completion data stored as JSONB';
COMMENT ON COLUMN reports.activity_data IS 'Weekly activity data stored as JSONB';
COMMENT ON COLUMN reports.remarks IS 'Teacher feedback and remarks for the student';
COMMENT ON COLUMN reports.report_type IS 'Type of report (progress, assessment, quiz, etc.)';
COMMENT ON COLUMN reports.status IS 'Current status of the report (active, archived, deleted)';
COMMENT ON COLUMN reports.created_at IS 'When the report was first created';
COMMENT ON COLUMN reports.updated_at IS 'When the report was last updated';
COMMENT ON COLUMN reports.generated_at IS 'When the PDF was generated';
COMMENT ON COLUMN reports.expires_at IS 'Optional expiration date for the report';

-- Example data structure for JSONB columns:
/*
report_data example:
{
  "student_name": "John Doe",
  "total_score": 85,
  "overall_percentage": 85.5,
  "subjects": ["Math", "Science", "English"],
  "charts": {
    "subject_mastery": {...},
    "topic_completion": {...},
    "weekly_activity": {...}
  },
  "summary": "Excellent progress in all subjects...",
  "recommendations": ["Continue practicing math", "Focus on science labs"]
}

subject_scores example:
{
  "Math": 90,
  "Science": 85,
  "English": 80,
  "History": 88,
  "Computer Science": 92
}

topic_completion example:
{
  "Math": {
    "completed": 15,
    "total": 20,
    "percentage": 75
  },
  "Science": {
    "completed": 18,
    "total": 22,
    "percentage": 82
  }
}

activity_data example:
{
  "weekly_activity": [
    {"day": "Monday", "activities": 3},
    {"day": "Tuesday", "activities": 5},
    {"day": "Wednesday", "activities": 4}
  ],
  "total_activities": 25,
  "average_daily": 3.6
}
*/ 