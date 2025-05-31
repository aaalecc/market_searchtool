"""
Script to clear all items from the database.
"""

from core.database import db

def main():
    with db.get_connection() as conn:
        # Delete all items from search_results table
        conn.execute("DELETE FROM search_results")
        conn.commit()
        print("All items have been deleted from the database.")

if __name__ == "__main__":
    main() 