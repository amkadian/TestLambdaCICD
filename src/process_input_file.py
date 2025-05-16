import csv
import psycopg2
import os

def process_input_file(file_path):
    # Database connection parameters (can be configured via environment variables for cloud deployment)
    db_config = {
        'dbname': os.getenv('DB_NAME', 'amkadian'),
        'user': os.getenv('DB_USER', 'amkadian'),
        'password': os.getenv('DB_PASSWORD', ''),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }

    # Counters for statistics
    records_processed = 0
    records_skipped = 0
    records_inserted = 0

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        print("Connected to the database successfully.")

        # Open the CSV file
        with open(file_path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            # Skip the header row if present
            next(csv_reader, None)
            
            for row in csv_reader:
                records_processed += 1
                author_id = int(row[0])
                author_pen_name = row[1]
                book_id = int(row[2])
                book_name = row[3]

                # Check if the author exists
                cursor.execute("SELECT author_id FROM public.authors WHERE author_id = %s AND author_pen_name = %s", (author_id, author_pen_name))
                author_exists = cursor.fetchone()

                # Check if the book exists
                cursor.execute("SELECT book_id FROM public.books WHERE book_id = %s AND book_name = %s", (book_id, book_name))
                book_exists = cursor.fetchone()

                if author_exists and book_exists:
                    # Both author and book exist, skip the record
                    records_skipped += 1
                    print(f"Record already exists: Author '{author_pen_name}' and Book '{book_name}'")
                else:
                    # Insert into authors table if the author does not exist
                    if not author_exists:
                        cursor.execute("INSERT INTO public.authors (author_id, author_pen_name) VALUES (%s, %s)", (author_id, author_pen_name))
                        print(f"Inserted author: {author_pen_name}")

                    # Insert into books table if the book does not exist
                    if not book_exists:
                        cursor.execute("INSERT INTO public.books (book_id, book_name) VALUES (%s, %s)", (book_id, book_name))
                        print(f"Inserted book: {book_name}")

                    # Insert into library table
                    cursor.execute("INSERT INTO public.library (book_id, author_id) VALUES (%s, %s)", (book_id, author_id))
                    print(f"Inserted into library: Book '{book_name}' by Author '{author_pen_name}'")

                    records_inserted += 1

            # Commit the transaction
            conn.commit()
            print("All records processed and committed successfully.")

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except psycopg2.Error as db_error:
        print(f"Database error: {db_error}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("Database connection closed.")

        # Print statistics
        print("\n=== Processing Statistics ===")
        print(f"Total records processed: {records_processed}")
        print(f"Records skipped (already exist): {records_skipped}")
        print(f"Records inserted: {records_inserted}")

# Replace 'sample_books_authors.csv' with the path to your CSV file
file_path = './data/sample_books_authors.csv'
process_input_file(file_path)