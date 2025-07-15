#!/usr/bin/env python3
"""
Database migration script to add new fields to existing MemoryEntry objects
"""

import sqlite3
import json
from pathlib import Path

def migrate_database(db_path: str = "agent_memory.db"):
    """Migrate existing database to add new fields"""
    print(f"Migrating database: {db_path}")
    
    if not Path(db_path).exists():
        print("Database file does not exist. Nothing to migrate.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Check if new columns exist
            cursor = conn.execute("PRAGMA table_info(memories)")
            columns = [column[1] for column in cursor.fetchall()]
            
            print(f"Existing columns: {columns}")
            
            # Add new columns if they don't exist
            if 'importance' not in columns:
                print("Adding importance column...")
                conn.execute("ALTER TABLE memories ADD COLUMN importance REAL DEFAULT 5.0")
            
            if 'tags' not in columns:
                print("Adding tags column...")
                conn.execute("ALTER TABLE memories ADD COLUMN tags TEXT")
            
            if 'last_accessed' not in columns:
                print("Adding last_accessed column...")
                conn.execute("ALTER TABLE memories ADD COLUMN last_accessed TEXT")
            
            # Update existing records to have default values
            print("Updating existing records...")
            conn.execute("UPDATE memories SET importance = 5.0 WHERE importance IS NULL")
            conn.execute("UPDATE memories SET tags = '[]' WHERE tags IS NULL")
            
            # Commit changes
            conn.commit()
            
            print("Database migration completed successfully!")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    migrate_database() 