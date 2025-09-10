-- Users Table Schema for Neon DB
-- This table stores user authentication and profile information

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'student',
    email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_users_role_active ON users(role, is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

-- Full-text search index for username and email (if using PostgreSQL)
CREATE INDEX IF NOT EXISTS idx_users_search_fts ON users USING gin(to_tsvector('english', username || ' ' || COALESCE(email, '')));

-- Trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_users_updated_at();

-- Comments for documentation
COMMENT ON TABLE users IS 'Stores user authentication and profile information';
COMMENT ON COLUMN users.id IS 'Unique identifier for the user';
COMMENT ON COLUMN users.username IS 'Unique username for login';
COMMENT ON COLUMN users.password IS 'Hashed password using bcrypt';
COMMENT ON COLUMN users.role IS 'User role (student, teacher, admin)';
COMMENT ON COLUMN users.email IS 'User email address (optional)';
COMMENT ON COLUMN users.created_at IS 'When the user account was created';
COMMENT ON COLUMN users.updated_at IS 'When the user account was last updated';
COMMENT ON COLUMN users.last_login IS 'When the user last logged in';
COMMENT ON COLUMN users.is_active IS 'Whether the user account is active';

-- Sample data (for testing)
INSERT INTO users (username, password, role, email) VALUES
('student1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxq3Hy', 'student', 'student1@example.com'),
('teacher1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxq3Hy', 'teacher', 'teacher1@example.com'),
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxq3Hy', 'teacher', 'admin@example.com')
ON CONFLICT (username) DO NOTHING;

-- Note: The password hash above is for 'pass' - in production, use proper password hashing 