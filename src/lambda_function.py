import json
import csv
import psycopg2
import os
import boto3

def lambda_handler(event, context):
    # Database connection parameters (configured via environment variables)
    db_config = {
        'dbname': os.getenv('DB_NAME', 'amkadian'),
        'user': os.getenv('DB_USER', 'amkadian'),
        'password': os.getenv('DB_PASSWORD', ''),
        'host': os.getenv('DB_HOST', 'your-aurora-endpoint'),
        'port': os.getenv('DB_PORT', '5432')
    }

    # S3 bucket and file details (from event or environment variables)
    bucket_name = os.getenv('S3_BUCKET_NAME', 'your-bucket-name')
    file_key = os.getenv('S3_FILE_KEY', 'path/to/your_file.csv')

    # Counters for statistics
    records_processed = 0
    records_skipped = 0
    records_inserted = 0

    try:
        # Connect to the Aurora PostgreSQL database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        print("Connected to the Aurora PostgreSQL database successfully.")

        # Download the file from S3
        s3 = boto3.client('s3')
        local_file_path = '/tmp/input_file.csv'  # Lambda's /tmp directory
        s3.download_file(bucket_name, file_key, local_file_path)
        print(f"File downloaded from S3: {bucket_name}/{file_key}")

        # Open the CSV file
        with open(local_file_path, mode='r') as csv_file:
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
        print(f"Error: The file at {file_key} was not found in bucket {bucket_name}.")
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

        # Return statistics as the Lambda response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Processing completed successfully.',
                'records_processed': records_processed,
                'records_skipped': records_skipped,
                'records_inserted': records_inserted
            })
        }