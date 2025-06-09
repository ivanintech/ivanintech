import sqlite3
import os
from datetime import datetime

# Define database paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Should point to backend/
OLD_DB_PATH = os.path.join(BASE_DIR, 'ivanintech_old.db')
NEW_DB_PATH = os.path.join(BASE_DIR, 'ivanintech.db')

# Columns for the resource_links table in the new database
# Based on alembic migration a21dbe96b72e_create_resource_links_table.py
NEW_DB_COLUMNS = [
    'id', 'title', 'url', 'ai_generated_description', 'personal_note',
    'resource_type', 'tags', 'thumbnail_url', 'created_at'
]

def get_table_columns(conn, table_name):
    """Fetches column names for a given table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    return [row[1] for row in cursor.fetchall()]

def migrate_data():
    """Migrates data from the old database to the new database."""
    print(f"Old database path: {OLD_DB_PATH}")
    print(f"New database path: {NEW_DB_PATH}")

    if not os.path.exists(OLD_DB_PATH):
        print(f"Error: Old database not found at {OLD_DB_PATH}")
        return

    # Connect to the old database
    old_conn = sqlite3.connect(OLD_DB_PATH)
    old_cursor = old_conn.cursor()

    # Connect to the new database
    new_conn = sqlite3.connect(NEW_DB_PATH)
    new_cursor = new_conn.cursor()

    # --- Migrate resource_links table ---
    old_table_name = 'resource_links' # Assuming this is the table name in the old DB
    new_table_name = 'resource_links'

    try:
        # Check if the table exists in the old database
        old_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{old_table_name}';")
        if not old_cursor.fetchone():
            # Try common alternative names if 'resource_links' is not found
            alternative_names = ['resourcelinks', 'links', 'resources']
            found_alternative = False
            for alt_name in alternative_names:
                old_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{alt_name}';")
                if old_cursor.fetchone():
                    old_table_name = alt_name
                    print(f"Found table '{old_table_name}' in the old database instead of 'resource_links'.")
                    found_alternative = True
                    break
            if not found_alternative:
                print(f"Error: Table '{old_table_name}' (and common alternatives) not found in the old database at {OLD_DB_PATH}.")
                return

        # Get columns from the old table
        old_columns = get_table_columns(old_conn, old_table_name)
        print(f"Columns in old table '{old_table_name}': {old_columns}")

        # Fetch data from the old table
        old_cursor.execute(f"SELECT * FROM {old_table_name};")
        rows = old_cursor.fetchall()
        print(f"Found {len(rows)} rows in {old_table_name} from old database.")

        if not rows:
            print(f"No data to migrate from {old_table_name}.")
            return

        # Prepare data for insertion
        # We need to map old columns to new columns
        # For simplicity, this script assumes that if a column exists in both, the data is compatible.
        # More complex transformations would require more specific logic here.

        successful_inserts = 0
        failed_inserts = 0

        for row_index, row_data in enumerate(rows):
            insert_data = {}
            for i, col_name in enumerate(old_columns):
                if col_name in NEW_DB_COLUMNS:
                    # Handle datetime conversion for created_at if it's a string
                    if col_name == 'created_at' and isinstance(row_data[i], str):
                        try:
                            # Attempt to parse common ISO formats
                            dt_obj = datetime.fromisoformat(row_data[i].replace('Z', '+00:00'))
                            insert_data[col_name] = dt_obj
                        except ValueError:
                            try:
                                # Try another common format like 'YYYY-MM-DD HH:MM:SS.ffffff'
                                dt_obj = datetime.strptime(row_data[i], '%Y-%m-%d %H:%M:%S.%f')
                                insert_data[col_name] = dt_obj
                            except ValueError:
                                print(f"Warning: Could not parse date string '{row_data[i]}' for 'created_at' in row {row_index}. Setting to None.")
                                insert_data[col_name] = None # Or a default date, or skip row
                    else:
                        insert_data[col_name] = row_data[i]
                elif col_name == 'Id' and 'id' in NEW_DB_COLUMNS : # Handle case sensitivity for 'Id' -> 'id'
                    insert_data['id'] = row_data[i]


            # Fill missing columns with None or default values
            for new_col in NEW_DB_COLUMNS:
                if new_col not in insert_data:
                    if new_col == 'created_at': # Default for created_at if missing entirely
                        insert_data[new_col] = datetime.utcnow()
                    else:
                        insert_data[new_col] = None

            # Ensure all required columns for the new schema are present
            # 'id', 'title', 'url', 'created_at' are non-nullable based on alembic
            if not all(k in insert_data and insert_data[k] is not None for k in ['id', 'title', 'url', 'created_at']):
                print(f"Skipping row {row_index} due to missing required fields (id, title, url, created_at): {insert_data}")
                failed_inserts += 1
                continue

            # Construct the insert query
            # Using INSERT OR IGNORE to skip duplicates based on primary key 'id'
            columns_to_insert = [col for col in NEW_DB_COLUMNS if col in insert_data]
            placeholders = ', '.join(['?'] * len(columns_to_insert))
            sql = f"INSERT OR IGNORE INTO {new_table_name} ({', '.join(columns_to_insert)}) VALUES ({placeholders});"
            values = [insert_data[col] for col in columns_to_insert]

            try:
                new_cursor.execute(sql, values)
                successful_inserts += 1
            except sqlite3.IntegrityError as e:
                print(f"IntegrityError for row {row_index} (ID: {insert_data.get('id')}): {e}. Data: {insert_data}")
                failed_inserts += 1
            except sqlite3.InterfaceError as e:
                print(f"InterfaceError for row {row_index} (ID: {insert_data.get('id')}): {e}. Check data types. Data: {insert_data}")
                failed_inserts += 1
            except Exception as e:
                print(f"An unexpected error occurred for row {row_index} (ID: {insert_data.get('id')}): {e}. Data: {insert_data}")
                failed_inserts += 1


        new_conn.commit()
        print(f"Migration for '{new_table_name}' complete. Successfully inserted: {successful_inserts}, Failed/Skipped: {failed_inserts}")

    except sqlite3.Error as e:
        print(f"SQLite error during migration: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        old_conn.close()
        new_conn.close()

if __name__ == '__main__':
    migrate_data() 