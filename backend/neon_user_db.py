import psycopg2
import psycopg2.extras
import os
import bcrypt
from typing import Optional, Dict, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NeonUserDatabase:
    def __init__(self, connection_string: str = None):
        """
        Initialize Neon DB connection for user management
        connection_string: Neon DB connection string
        """
        self.connection_string = connection_string or os.getenv('DATABASE_URL') or os.getenv('NEON_DB_URL')
        if not self.connection_string:
            raise ValueError("DATABASE_URL or NEON_DB_URL environment variable is required")
    
    def get_connection(self):
        """Get a database connection"""
        return psycopg2.connect(self.connection_string)
    
    def init_database(self):
        """Initialize the database with the users table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create the users table
            cursor.execute('''
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
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)')
            
            # Create trigger for updated_at
            cursor.execute('''
                CREATE OR REPLACE FUNCTION update_users_updated_at()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql'
            ''')
            
            cursor.execute('''
                DROP TRIGGER IF EXISTS update_users_updated_at ON users;
                CREATE TRIGGER update_users_updated_at 
                    BEFORE UPDATE ON users 
                    FOR EACH ROW 
                    EXECUTE FUNCTION update_users_updated_at()
            ''')
            
            conn.commit()
            print("✅ Users database initialized successfully")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error initializing users database: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_user(self, username: str, password: str, role: str = 'student', email: str = None) -> Dict:
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            if cursor.fetchone():
                raise ValueError("Username already exists")
            
            # Hash the password
            hashed_password = self.hash_password(password)
            
            # Insert new user
            cursor.execute('''
                INSERT INTO users (username, password, role, email)
                VALUES (%s, %s, %s, %s)
                RETURNING id, username, role, email, created_at
            ''', (username, hashed_password, role, email))
            
            user = cursor.fetchone()
            conn.commit()
            
            return dict(user)
            
        except Exception as e:
            conn.rollback()
            print(f"Error creating user: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate a user and return user data if successful"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # Get user by username
            cursor.execute('''
                SELECT id, username, password, role, email, created_at, last_login, is_active
                FROM users 
                WHERE username = %s AND is_active = TRUE
            ''', (username,))
            
            user = cursor.fetchone()
            if not user:
                return None
            
            # Verify password
            if not self.verify_password(password, user['password']):
                return None
            
            # Update last login
            cursor.execute('''
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP 
                WHERE id = %s
            ''', (user['id'],))
            
            conn.commit()
            
            # Return user data without password
            user_dict = dict(user)
            del user_dict['password']
            return user_dict
            
        except Exception as e:
            conn.rollback()
            print(f"Error authenticating user: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cursor.execute('''
                SELECT id, username, role, email, created_at, last_login, is_active
                FROM users 
                WHERE id = %s AND is_active = TRUE
            ''', (user_id,))
            
            user = cursor.fetchone()
            return dict(user) if user else None
            
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cursor.execute('''
                SELECT id, username, role, email, created_at, last_login, is_active
                FROM users 
                WHERE username = %s AND is_active = TRUE
            ''', (username,))
            
            user = cursor.fetchone()
            return dict(user) if user else None
            
        except Exception as e:
            print(f"Error getting user by username: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Build dynamic update query
            update_fields = []
            values = []
            
            allowed_fields = ['username', 'role', 'email', 'is_active']
            for key, value in kwargs.items():
                if key in allowed_fields:
                    update_fields.append(f"{key} = %s")
                    values.append(value)
            
            if not update_fields:
                return False
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor.execute(query, values)
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            print(f"Error updating user: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = self.hash_password(new_password)
            
            cursor.execute('''
                UPDATE users 
                SET password = %s 
                WHERE id = %s
            ''', (hashed_password, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            print(f"Error changing password: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def delete_user(self, user_id: int, soft_delete: bool = True) -> bool:
        """Delete a user (soft delete by default)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if soft_delete:
                cursor.execute('UPDATE users SET is_active = FALSE WHERE id = %s', (user_id,))
            else:
                cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            print(f"Error deleting user: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_all_users(self, active_only: bool = True) -> List[Dict]:
        """Get all users"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            if active_only:
                cursor.execute('''
                    SELECT id, username, role, email, created_at, last_login, is_active
                    FROM users 
                    WHERE is_active = TRUE
                    ORDER BY created_at DESC
                ''')
            else:
                cursor.execute('''
                    SELECT id, username, role, email, created_at, last_login, is_active
                    FROM users 
                    ORDER BY created_at DESC
                ''')
            
            users = cursor.fetchall()
            return [dict(user) for user in users]
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_users_by_role(self, role: str, active_only: bool = True) -> List[Dict]:
        """Get users by role"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            if active_only:
                cursor.execute('''
                    SELECT id, username, role, email, created_at, last_login, is_active
                    FROM users 
                    WHERE role = %s AND is_active = TRUE
                    ORDER BY created_at DESC
                ''', (role,))
            else:
                cursor.execute('''
                    SELECT id, username, role, email, created_at, last_login, is_active
                    FROM users 
                    WHERE role = %s
                    ORDER BY created_at DESC
                ''', (role,))
            
            users = cursor.fetchall()
            return [dict(user) for user in users]
            
        except Exception as e:
            print(f"Error getting users by role: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def search_users(self, search_term: str, active_only: bool = True) -> List[Dict]:
        """Search users by username or email"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            if active_only:
                cursor.execute('''
                    SELECT id, username, role, email, created_at, last_login, is_active
                    FROM users 
                    WHERE (username ILIKE %s OR email ILIKE %s) AND is_active = TRUE
                    ORDER BY created_at DESC
                ''', (f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute('''
                    SELECT id, username, role, email, created_at, last_login, is_active
                    FROM users 
                    WHERE username ILIKE %s OR email ILIKE %s
                    ORDER BY created_at DESC
                ''', (f'%{search_term}%', f'%{search_term}%'))
            
            users = cursor.fetchall()
            return [dict(user) for user in users]
            
        except Exception as e:
            print(f"Error searching users: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_user_statistics(self) -> Dict:
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_users,
                    COUNT(CASE WHEN role = 'student' THEN 1 END) as students,
                    COUNT(CASE WHEN role = 'teacher' THEN 1 END) as teachers,
                    COUNT(CASE WHEN last_login >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as recent_logins
                FROM users
            ''')
            
            stats = cursor.fetchone()
            return {
                'total_users': stats[0],
                'active_users': stats[1],
                'students': stats[2],
                'teachers': stats[3],
                'recent_logins': stats[4]
            }
            
        except Exception as e:
            print(f"Error getting user statistics: {e}")
            raise
        finally:
            cursor.close()
            conn.close() 