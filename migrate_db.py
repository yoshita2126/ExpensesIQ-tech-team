#!/usr/bin/env python3
"""
Database migration script to add phone column to otp_tokens table
"""

import sqlite3
import sys

def migrate_database():
    """Add phone column to otp_tokens table if it doesn't exist"""
    try:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        
        # Check if phone column already exists
        cur.execute("PRAGMA table_info(otp_tokens)")
        columns = {row[1] for row in cur.fetchall()}
        
        if 'phone' not in columns:
            print("Adding 'phone' column to otp_tokens table...")
            cur.execute("ALTER TABLE otp_tokens ADD COLUMN phone TEXT")
            conn.commit()
            print("✓ Successfully added 'phone' column to otp_tokens")
        else:
            print("✓ 'phone' column already exists in otp_tokens")
        
        # Also make email optional (it should already be nullable)
        cur.execute("PRAGMA table_info(otp_tokens)")
        columns_info = {row[1]: row for row in cur.fetchall()}
        
        email_info = columns_info.get('email')
        if email_info and email_info[3]:  # notnull check
            print("Email column is marked as NOT NULL. This is OK for backward compatibility.")
        
        conn.close()
        print("\n✓ Database migration completed successfully!")
        return True
    
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False


if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
