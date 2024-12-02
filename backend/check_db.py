import sqlite3

def check_db_structure(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Found tables:", [table[0] for table in tables])
        
        # Check structure of each table
        for table in tables:
            table_name = table[0]
            print(f"\nStructure of {table_name}:")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
                
    except sqlite3.Error as e:
        print(f"Error accessing database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_db_structure("allcountries.sqlite3")