External Drive Indexer

A lightweight Python utility designed to automatically detect mounted external drives and index their file metadata into a local SQLite database.
Features

    Auto-Detection: Uses lsblk to identify hotplugged (external) devices while filtering out system partitions.

    Efficient Indexing: Recursively walks drive directories and captures file names, paths, sizes, and modification timestamps.

    Persistent Storage: Saves all data into a structured SQLite3 database (storage_index.db) for easy querying.

How It Works

The script follows a logical execution flow:

    Setup: Initializes the SQLite database and file_index table.

    Scan: Queries the system for mounted external mount points.

    Process: Iterates through every file on the detected drives.

    Log: Commits the metadata to the database and provides progress updates in the terminal.

Requirements

    OS: Linux (requires lsblk).

    Python: 3.6+

    Permissions: Ensure the user has read permissions for the target external drives.

Usage

Simply run the script from your terminal:
Bash

python3 indexer3.py
