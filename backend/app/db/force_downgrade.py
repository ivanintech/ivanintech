import sqlite3
import os

# --- CONFIGURATION ---
# The path is relative to the 'backend' directory
DATABASE_FILE = "ivanintech.db"
TARGET_REVISION = "dfa5ec2e84d4" # The last known good revision
# ---------------------

print(f"Searching for the database at: {os.path.abspath(DATABASE_FILE)}")

if not os.path.exists(DATABASE_FILE):
    print(f"Error: The database file '{DATABASE_FILE}' was not found.")
    exit(1)

print(f"Attempting to connect to the database: {DATABASE_FILE}")
try:
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    print("Connection successful. Checking the current Alembic version...")

    # Check the current version
    cursor.execute("SELECT version_num FROM alembic_version")
    current_version = cursor.fetchone()
    if current_version:
        print(f"Current Alembic version: {current_version[0]}")
    else:
        print("No Alembic version found. Has Alembic been initialized on this DB?")
        exit(1)

    # Update to the desired version
    print(f"Updating Alembic version to: {TARGET_REVISION}")
    cursor.execute("UPDATE alembic_version SET version_num = ?", (TARGET_REVISION,))
    
    conn.commit()
    print("Version updated successfully.")

    # Verify the change
    cursor.execute("SELECT version_num FROM alembic_version")
    new_version = cursor.fetchone()
    print(f"Verified new Alembic version: {new_version[0]}")

    if new_version[0] == TARGET_REVISION:
        print("The script completed successfully!")
    else:
        print("Error: The version does not seem to have been updated correctly.")

except sqlite3.Error as e:
    print(f"SQLite error: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Database connection closed.") 