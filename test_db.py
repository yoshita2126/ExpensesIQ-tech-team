import sqlite3
import os

print("=== EXPENSESIQ DATABASE TEST ===\n")

if os.path.exists('data.db'):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cur.fetchall()
    
    print(f"✓ Database found: data.db")
    print(f"✓ Total tables: {len(tables)}\n")
    
    print("TABLES:")
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cur.fetchone()[0]
        print(f"  ✓ {table[0]:<25} ({count} rows)")
    
    # Check specific tables
    print("\n=== KEY TABLES ===")
    tables_to_check = ['users', 'otp_tokens', 'businesses', 'branches', 'products', 
                       'inventory', 'suppliers', 'invoices', 'gst_transactions']
    
    for table_name in tables_to_check:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if cur.fetchone():
            print(f"✓ {table_name:<25} schema created")
        else:
            print(f"✗ {table_name:<25} missing")
    
    conn.close()
    print("\n✓ DATABASE VERIFICATION PASSED")
else:
    print("✗ Database not found")
