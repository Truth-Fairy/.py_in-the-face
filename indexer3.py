import sqlite3
import subprocess
import json
import os
from datetime import datetime

DATABASE_NAME = "storage_index.db"

def setup_database():
    """Connects to the database and creates the necessary table."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_index (
            id INTEGER PRIMARY KEY,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            date_modified REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print(f"Database {DATABASE_NAME} and table 'file_index' created successfully.")

def get_mounted_drives():
    """Executes lsblk to find mounted external drives and returns their paths."""
    lsblk_command = ['lsblk', '-o', 'mountpoint,hotplug', '-J']
    
    try:
        result = subprocess.run(
            lsblk_command,
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Error running lsblk: {e}")
        return []
    except json.JSONDecodeError:
        print("Error: Could not parse lsblk output as JSON.")
        return []
    
    detected_paths = []
    
    if 'blockdevices' in data:
        for device in data['blockdevices']:
            mount_point = device.get('mountpoint')
            
            if mount_point and device.get('hotplug') == True:
                excluded = ('/', '/boot', '/swap')
                system_prefixes = ('/boot', '/efi', '/dev')
                
                if mount_point not in excluded and not mount_point.startswith(system_prefixes):
                    detected_paths.append(mount_point)
                    
    return detected_paths

def index_files(drive_paths):
    """Walks through each drive path and indexes all files into the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    total_files = 0
    
    for drive_path in drive_paths:
        print(f"Scanning drive: {drive_path}")
        
        try:
            for root, dirs, files in os.walk(drive_path):
                for filename in files:
                    try:
                        full_path = os.path.join(root, filename)
                        file_size = os.path.getsize(full_path)
                        date_modified = os.path.getmtime(full_path)
                        
                        cursor.execute("""
                            INSERT INTO file_index (file_path, file_name, file_size, date_modified)
                            VALUES (?, ?, ?, ?)
                        """, (full_path, filename, file_size, date_modified))
                        
                        total_files += 1
                        
                        if total_files % 100 == 0:
                            print(f"Indexed {total_files} files so far...")
                            
                    except (OSError, PermissionError) as e:
                        print(f"Skipping file {filename}: {e}")
                        continue
                        
        except (OSError, PermissionError) as e:
            print(f"Error accessing drive {drive_path}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"Indexing complete! Total files indexed: {total_files}")

if __name__ == "__main__":
    setup_database()
    drives = get_mounted_drives()
    print(f"Detected external drives: {drives}")
    
    if drives:
        index_files(drives)
    else:
        print("No external drives detected. Nothing to index.")
