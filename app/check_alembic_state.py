#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from database.connection import sync_engine
from sqlalchemy import text, inspect
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext

def check_database_state():
    """Check the current state of database vs Alembic tracking."""
    
    with sync_engine.connect() as connection:
        inspector = inspect(connection)
        
        print("🔍 Current Database Tables:")
        tables = inspector.get_table_names()
        for table in sorted(tables):
            print(f"  ✓ {table}")
            
        print(f"\n📊 Total tables found: {len(tables)}")
        
        # Check Alembic version table
        print("\n🔍 Alembic Version Table:")
        try:
            result = connection.execute(text("SELECT version_num FROM alembic_version")).fetchall()
            if result:
                print(f"  ✓ Current Alembic revision: {result[0][0]}")
            else:
                print("  ⚠️  No version found in alembic_version table")
        except Exception as e:
            print(f"  ❌ Alembic version table issue: {e}")
            
        # Check specific tables that are causing issues
        problem_tables = ['carbonleap.job_definitions', 'carbonleap.job_runs']
        print(f"\n🔍 Checking Problem Tables:")
        for table in problem_tables:
            if table in tables:
                print(f"  ✓ {table} exists in database")
                # Get column info
                columns = inspector.get_columns(table)
                print(f"    Columns: {[col['name'] for col in columns]}")
            else:
                print(f"  ❌ {table} NOT found in database")

if __name__ == "__main__":
    check_database_state()