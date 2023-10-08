import mysql.connector
import csv
import os
from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path

def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--db", type=str, default='database-1', help="database name")
    # Allow multiple table names as input
    parser.add_argument("--tables", type=str, nargs='+', default=['comments', 'likes', 'post_tags', 'posts', 'tags', 'users'], help="table names")
    args = parser.parse_args()
    return args

def fetch_table_data(db, table):
    try:
        cnx = mysql.connector.MySQLConnection(
            host="",
            database=db,
            user="",
            password=""
        )
        print("Connected successfully!")  # Print message on successful connection
    except mysql.connector.Error as err:
        print(f"Failed to connect! Error: {err}")
        return [], []

    cursor = cnx.cursor()
    cursor.execute(f"SELECT * FROM {table}")

    header = [row[0] for row in cursor.description]
    rows = cursor.fetchall()

    cnx.close()

    print(f"Fetched {len(rows)} rows from {table}")
    return header, rows

def main(args):
    # Get today's date in a specific format (e.g., YYYY-MM-DD)
    today_date = datetime.now().strftime("%Y-%m-%d")
    # Create a directory with today's date as its name
    folder_path = Path("./data") / today_date
    folder_path.mkdir(exist_ok=True, parents=True)
    
    for table in args.tables:
        header, rows = fetch_table_data(args.db, table)
        
        target_path = folder_path / (table + ".csv")
        with open(target_path, "w", newline='') as outfile:
            csv_writer = csv.writer(outfile)
            csv_writer.writerow(header)
            csv_writer.writerows(rows)
    
        print(f"Exported database {args.db} table {table} to {str(target_path)}")

if __name__ == "__main__":
    args = parse_args()
    main(args)
