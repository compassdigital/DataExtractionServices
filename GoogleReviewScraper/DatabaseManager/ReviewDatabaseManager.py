import sqlite3
import hashlib
import csv

class ReviewsDatabaseManager:
    def __init__(self, config):
        """
        Initializes an instance of the RestaurantReviewsDatabase class.

        :param config: Dictionary containing configuration settings.
        """
        self.config = config
        self.database_name = config['database_name']
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        """
        Creates a table in the SQLite database if it doesn't already exist.

        This function connects to the database, creates a 'reviews' table if
        it doesn't exist, and defines the table's schema.

        :return: None
        """
        connection= sqlite3.connect(self.database_name)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                review TEXT NOT NULL,
                time TEXT,
                diner_info TEXT,
                extra_info TEXT,
                hash TEXT NOT NULL UNIQUE,
                place_id TEXT NOT NULL,
                name TEXT NOT NULL,
                vicinity TEXT NOT NULL,
                rating REAL NOT NULL,
                zip_code INTEGER NOT NULL,
                price_level REAL,
                user_ratings_total INTEGER,
                category TEXT NOT NULL,
                url TEXT NOT NULL
            )
        ''')

        connection.commit()
        connection.close()

    def hash_review_data(self, review):
        """
        Hashes the given review using the SHA-256 algorithm.

        This function takes input review, encodes it as a string, and computes
        its SHA-256 hash, returning the hexadecimal digest.

        :param data: The review to be hashed.
        :return: Hexadecimal digest of the SHA-256 hash.
        :usage: Hexadecimal digest is passed into the database and used to determin if the review was already added into the database
        """
        hash_object = hashlib.sha256(str(review).encode())
        return hash_object.hexdigest()

    def review_exists(self, hash_value):
        """
        Checks if a review with the given hash value exists in the database.

        This function queries the 'reviews' table to check if a review with the
        specified hash value exists.

        :param hash_value: The hash value to check.
        :return: True if a review with the hash value exists, False otherwise.
        """
        try:
            connection= sqlite3.connect(self.database_name)
            cursor = connection.cursor()

            cursor.execute('SELECT COUNT(*) FROM reviews WHERE hash = ?', (hash_value,))
            count = cursor.fetchone()[0]

            return count > 0
        except sqlite3.Error as e:
            print(f"Error checking if review exists: {e}")
            return False


    def insert_review(self, data):
        """
        Checks if a review with the given hash value exists in the database.

        This function queries the 'reviews' table to check if a review with the
        specified hash value exists.

        :param hash_value: The hash value to check.
        :return: True if a review with the hash value exists, False otherwise.
        """
        hash_value = self.hash_review_data(data)
        
        if self.review_exists(hash_value):
            return

        try:
            connection = sqlite3.connect(self.database_name)
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO reviews (
                    review, hash, place_id, time, diner_info, extra_info, name, vicinity, rating, zip_code,
                    price_level, user_ratings_total, category, url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['review'], hash_value, data['place_id'], data['time'], data['diner_info'],
                data['extra_info'], data['name'], data['vicinity'], data['rating'],
                data['zip_code'], data['price_level'], data['user_ratings_total'],
                data['category'], data['url']
            ))
            connection.commit()
            print("Review successfully inserted.")
        except sqlite3.Error as e:
            print(f"Error during insertion: {e}")
    
    def clear_sitemap_database(self):
        """
        NOTE:FOR TESTING USE ONLY
        
        Clears all data from the 'sitemap' table in the SQLite database.

        This function removes all records from the 'sitemap' table.

        :return: None
        """
        try:
            connection = sqlite3.connect(self.database_name)
            cursor = connection.cursor()
            cursor.execute('DELETE FROM sitemap')
            connection.commit()
            print("All data removed from the sitemap table.")
        except sqlite3.Error as e:
            print("Error during data removal:", e)
           
    def save_and_clear_database(self, csv_filename='reviews_backup.csv'):
        """
        NOTE:FOR TESTING USE ONLY
        
        Saves records from the 'reviews' table to a CSV file and clears the table.

        This function retrieves all records from the 'reviews' table, saves them
        to a CSV file, and then deletes all records from the 'reviews' table.

        :param csv_filename: The filename for the CSV file (default: 'reviews_backup.csv').
        :return: None
        """
        connection = sqlite3.connect(self.database_name)
        cursor = connection.cursor()

        # Fetch all records from the 'reviews' table
        cursor.execute('SELECT * FROM reviews')
        records = cursor.fetchall()

        # Save records to CSV file
        with open(self.config['db_to_csv'], 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            # Write header
            csv_writer.writerow([description[0] for description in cursor.description])
            # Write data
            csv_writer.writerows(records)

        # Clear the 'reviews' table
        cursor.execute('DELETE FROM reviews')
        connection.commit()

        connection.close()
        print(f"Data saved to {self.config['db_to_csv']} and cleared from the database.")

