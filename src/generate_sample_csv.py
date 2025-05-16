import csv
import random

def generate_sample_csv(file_path, num_records=100):
    # Sample data for books and authors
    book_names = [f"Book_{i}" for i in range(1, num_records + 1)]
    author_names = [f"Author_{i}" for i in range(1, num_records + 1)]

    # Open the CSV file for writing
    with open(file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Write the header row
        csv_writer.writerow(["book_id", "book_name", "author_id", "author_pen_name"])
        
        # Generate records
        for i in range(1, num_records + 1):
            book_id = i
            book_name = random.choice(book_names)
            author_id = i
            author_pen_name = random.choice(author_names)
            
            # Write the record to the CSV
            csv_writer.writerow([book_id, book_name, author_id, author_pen_name])

    print(f"Sample CSV file with {num_records} records generated at: {file_path}")

# Generate the sample CSV file
file_path = './data/sample_books_authors.csv'
generate_sample_csv(file_path)