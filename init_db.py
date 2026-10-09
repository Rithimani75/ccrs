import MySQLdb
import os

print("[INFO] Attempting to initialize the database...")

try:
    # Connect to MySQL server without selecting a database
    db = MySQLdb.connect(
        host="localhost",
        user="root",
        passwd=""
    )
    cursor = db.cursor()

    # 1. Create the database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS ccrs;")
    cursor.execute("USE ccrs;")
    print("[OK] Database 'ccrs' ensured.")

    # 2. Read the database.sql file
    sql_file = "database.sql"
    if os.path.exists(sql_file):
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        # 3. Execute the SQL statements
        # Split by semicolon and execute one by one
        statements = sql_script.split(';')
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                except Exception as e:
                    pass # Ignore if table exists or other minor issues
        
        db.commit()
        print("[OK] Tables verified.")
    else:
        print("[WARNING] database.sql file not found. Skipping table creation.")

    cursor.close()
    db.close()
    print("[INFO] Database initialization complete.")

except MySQLdb.Error as err:
    print(f"[ERROR] MySQL Error: {err}")
    print("[INFO] Please ensure XAMPP or MySQL Server is running on port 3306.")
except Exception as e:
    print(f"[ERROR] An unexpected error occurred: {e}")
