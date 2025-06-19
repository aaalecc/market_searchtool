"""
Script to clear all data from the database.
"""

import sys
from core.database import clear_all_tables

def main():
    print("Are you sure you want to clear all data from the database?")
    print("This will delete all saved searches, search results, and settings.")
    response = input("Type 'yes' to confirm: ")
    
    if response.lower() == 'yes':
        print("\nClearing database...")
        clear_all_tables()
        print("Database cleared successfully.")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main() 