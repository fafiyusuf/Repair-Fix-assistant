"""
Database migration script to add new columns for improved token tracking.

This script updates the usage_stats table to include separate tracking
for input and output tokens.

Usage:
    python scripts/migrate_token_columns.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Run the database migration."""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    print("🔄 Connecting to Supabase...")
    
    try:
        # This won't work directly with Supabase client as it doesn't support DDL
        # Instructions for manual execution instead
        
        migration_sql = """
-- Migration: Add token detail columns to usage_stats
-- Run this SQL in your Supabase SQL Editor

ALTER TABLE usage_stats 
ADD COLUMN IF NOT EXISTS input_tokens INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS output_tokens INTEGER DEFAULT 0;

-- Update existing records to split tokens_used into input/output
-- Approximate split: 40% input, 60% output (typical ratio)
UPDATE usage_stats 
SET 
    input_tokens = CAST(tokens_used * 0.4 AS INTEGER),
    output_tokens = CAST(tokens_used * 0.6 AS INTEGER)
WHERE input_tokens = 0 AND output_tokens = 0;

-- Add comment
COMMENT ON COLUMN usage_stats.input_tokens IS 'Number of tokens in the user input';
COMMENT ON COLUMN usage_stats.output_tokens IS 'Number of tokens in the assistant response';
"""
        
        print("\n" + "="*70)
        print("📋 MANUAL MIGRATION REQUIRED")
        print("="*70)
        print("\nPlease copy the following SQL and run it in your Supabase SQL Editor:")
        print("\n" + migration_sql)
        print("\n" + "="*70)
        print("\n✅ After running the SQL, the migration will be complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting database migration...")
    print("📊 Adding input_tokens and output_tokens columns to usage_stats table\n")
    
    success = run_migration()
    
    if success:
        print("\n✅ Migration instructions displayed successfully!")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
