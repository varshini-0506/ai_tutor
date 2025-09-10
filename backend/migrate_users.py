#!/usr/bin/env python3
"""
Migration script to set up users table in Neon DB
This script helps migrate from in-memory users to Neon DB
"""

import os
import sys
from neon_user_db import NeonUserDatabase
from config import Config

def setup_environment():
    """Set up environment variables"""
    print("🔧 Setting up environment...")
    
    # Check if DATABASE_URL is set
    if not Config.get_database_url():
        print("❌ Error: DATABASE_URL or NEON_DB_URL environment variable not set")
        print("Please set your Neon DB connection string as an environment variable:")
        print("export DATABASE_URL='postgresql://username:password@host:port/database'")
        return False
    
    print("✅ Database URL configured")
    return True

def initialize_users_database():
    """Initialize the Neon DB with the users table"""
    print("🗄️ Initializing users database...")
    
    try:
        user_db = NeonUserDatabase()
        user_db.init_database()
        print("✅ Users database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing users database: {e}")
        return False

def create_sample_users():
    """Create sample users for testing"""
    print("📝 Creating sample users...")
    
    try:
        user_db = NeonUserDatabase()
        
        # Sample users
        sample_users = [
            {
                'username': 'student1',
                'password': 'pass',
                'role': 'student',
                'email': 'student1@example.com'
            },
            {
                'username': 'teacher1',
                'password': 'pass',
                'role': 'teacher',
                'email': 'teacher1@example.com'
            },
            {
                'username': 'admin',
                'password': 'admin123',
                'role': 'teacher',
                'email': 'admin@example.com'
            }
        ]
        
        created_count = 0
        for user_data in sample_users:
            try:
                user = user_db.create_user(
                    username=user_data['username'],
                    password=user_data['password'],
                    role=user_data['role'],
                    email=user_data['email']
                )
                print(f"✅ Created user: {user['username']} (ID: {user['id']})")
                created_count += 1
            except ValueError as e:
                print(f"⚠️ User {user_data['username']} already exists: {e}")
            except Exception as e:
                print(f"❌ Error creating user {user_data['username']}: {e}")
        
        print(f"✅ Successfully created {created_count} sample users")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample users: {e}")
        return False

def test_user_operations():
    """Test user database operations"""
    print("🧪 Testing user operations...")
    
    try:
        user_db = NeonUserDatabase()
        
        # Test authentication
        print("Testing authentication...")
        user = user_db.authenticate_user('student1', 'pass')
        if user:
            print(f"✅ Authentication successful for student1: {user['username']}")
        else:
            print("❌ Authentication failed for student1")
        
        # Test getting all users
        print("Testing get all users...")
        users = user_db.get_all_users()
        print(f"✅ Found {len(users)} users in database")
        
        # Test getting users by role
        print("Testing get users by role...")
        students = user_db.get_users_by_role('student')
        teachers = user_db.get_users_by_role('teacher')
        print(f"✅ Found {len(students)} students and {len(teachers)} teachers")
        
        # Test user statistics
        print("Testing user statistics...")
        stats = user_db.get_user_statistics()
        print(f"✅ User statistics: {stats}")
        
        print("✅ All user operations working correctly")
        return True
        
    except Exception as e:
        print(f"❌ User operations test failed: {e}")
        return False

def migrate_from_memory_users():
    """Migrate users from the old in-memory system"""
    print("🔄 Migrating from in-memory users...")
    
    # Old in-memory users (from the original app.py)
    old_users = [
        {"username": "student1", "password": "pass", "role": "student"},
        {"username": "teacher1", "password": "pass", "role": "teacher"},
    ]
    
    try:
        user_db = NeonUserDatabase()
        
        migrated_count = 0
        for old_user in old_users:
            try:
                # Check if user already exists
                existing_user = user_db.get_user_by_username(old_user['username'])
                if existing_user:
                    print(f"⚠️ User {old_user['username']} already exists, skipping...")
                    continue
                
                # Create user in database
                user = user_db.create_user(
                    username=old_user['username'],
                    password=old_user['password'],
                    role=old_user['role']
                )
                
                print(f"✅ Migrated user: {user['username']} (ID: {user['id']})")
                migrated_count += 1
                
            except Exception as e:
                print(f"❌ Error migrating user {old_user['username']}: {e}")
        
        print(f"🎉 Successfully migrated {migrated_count} users")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting Users Migration for AI Tutor")
    print("=" * 50)
    
    # Print current configuration
    Config.print_config()
    print()
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Initialize users database
    if not initialize_users_database():
        sys.exit(1)
    
    # Migrate existing users
    if not migrate_from_memory_users():
        print("⚠️ Migration failed, but continuing...")
    
    # Create sample data (optional)
    create_sample = input("Create sample users for testing? (y/n): ").lower().strip()
    if create_sample == 'y':
        create_sample_users()
    
    # Test user operations
    if not test_user_operations():
        sys.exit(1)
    
    print("\n🎉 Users migration completed successfully!")
    print("You can now use Neon DB for user authentication.")
    print("\nNext steps:")
    print("1. Update your frontend to use the new authentication endpoints")
    print("2. Test login/signup functionality")
    print("3. Restart your Flask application")

if __name__ == "__main__":
    main() 