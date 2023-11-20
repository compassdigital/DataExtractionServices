import pandas as pd
import sqlite3
import threading
class SiteMapDabaseManager:
    
    def __init__(self,config):
        self.config = config
        self.database_name = self.config['sitemap_db_name']

    def create_sitemap_table_if_not_exists(self):
        """
        Creates a 'reviews' table in the SQLite database if it doesn't already exist.

        This method is called during the initialization of the class.
        :return: None
        """
        connection = sqlite3.connect(self.database_name , timeout=10)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sitemap (
                id INTEGER PRIMARY KEY,
                place_id TEXT,
                name TEXT,
                vicinity TEXT,
                rating REAL,
                zip_code INTEGER,
                price_level REAL,
                user_ratings_total INTEGER,
                category TEXT,
                url TEXT,
                status TEXT DEFAULT 'NOT RUNNING'
            )
        ''')
        connection.commit()
        connection.close()
    
    def insert_data_into_sitemap(self, sitemap_data):
        """
        Inserts data into the 'sitemap' table in the SQLite database.

        This method inserts data into the 'sitemap' table, including place information,
        rating, and other details. The 'status' column is set to 'NOT RUNNING' by default.

        :param sitemap_data: Dictionary containing sitemap data.
        :return: None
        """
        try:
            connection = sqlite3.connect(self.database_name , timeout=10)
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO sitemap (
                    place_id, name, vicinity, rating, zip_code, price_level,
                    user_ratings_total, category, url, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'NOT RUNNING')
            ''', (
                sitemap_data["place_id"], sitemap_data["name"], sitemap_data["vicinity"], sitemap_data['rating'],
                sitemap_data['zip_code'], sitemap_data['price_level'], sitemap_data['user_ratings_total'],
                sitemap_data['category'], sitemap_data['url']
            ))
            connection.commit()
            connection.close()
        except sqlite3.IntegrityError as e:
            print("Error during insertion. IntegrityError.")
        finally:
            connection.close()

    def select_random_sitemap_value(self):
        """
        Selects a random row from the 'sitemap' table with 'NOT RUNNING' status,
        updates its status to 'RUNNING', and returns the selected row.

        :return: Dictionary containing the selected row data or None if no row is selected.
        """
        try:
            connection = sqlite3.connect(self.database_name , timeout=10)
            cursor = connection.cursor()

            # Select a random row from the table
            cursor.execute(f'''
                SELECT *
                FROM sitemap
                WHERE status = 'NOT RUNNING'
                ORDER BY RANDOM()
                LIMIT 1;
            ''')

            # Fetch the data of the selected row
            selected_row = cursor.fetchone()
            if selected_row:
                column_names = [description[0] for description in cursor.description]
                updated_row = dict(zip(column_names,selected_row))

                cursor.execute('''
                    UPDATE sitemap
                    SET status = 'RUNNING'
                    WHERE id = ?;
                ''', (updated_row['id'],))
                connection.close()
                return updated_row  
        except sqlite3.Error as e:
            print(f"Error selecting and updating random row: {e}")
        finally:
            connection.close()

            
    def update_finished_job(self,record_id):
        """
        Updates the status to 'FINISH' for the row with the given ID in the 'sitemap' table.

        :param record_id: The ID of the row to be updated.
        :return: None
        """
        try:
            connection = sqlite3.connect(self.database_name , timeout=10)
            cursor = connection.cursor()
            # Update the status to 'FINISH' for the row with the given ID
            cursor.execute('''
                UPDATE sitemap
                SET status = 'FINISH'
                WHERE id = ?;
            ''', (record_id,))

            # Commit the changes to the database
            connection.commit()
        except sqlite3.Error as e:
            print(f"Error updating status: {e}")
        finally:
            connection.close()
    
    def update_failed_job(self,record_id):
        """
        Updates the status to 'NOT RUNNING' for the row with the given ID in the 'sitemap' table.

        :param record_id: The ID of the row to be updated.
        :return: None
        """
        try:
            connection = sqlite3.connect(self.database_name , timeout=10)
            cursor = connection.cursor()

            # Update the status to 'FINISH' for the row with the given ID
            cursor.execute('''
                UPDATE sitemap
                SET status = 'NOT RUNNING'
                WHERE id = ?;
            ''', (record_id,))
            # Commit the changes to the database
            connection.commit()

        except sqlite3.Error as e:
            print(f"Error updating status: {e}")
        finally:
            connection.close()
                        
    def clear_sitemap_table(self):
        """
        Clears all data from the 'sitemap' table in the SQLite database.

        This method removes all records from the 'sitemap' table.

        :return: None
        """
        try:
            connection = sqlite3.connect(self.database_name , timeout=10)
            cursor = connection.cursor()
            cursor.execute('DELETE FROM sitemap')
            connection.commit()
            print("All data removed from the sitemap table.")
            connection.close()
        except sqlite3.Error as e:
            print("Error during data removal:", e)

            

    def generate_sitemap(self):
        """
        Generates sitemap data from a CSV file and inserts it into the 'sitemap' table.

        This method reads data from a CSV file, generates URLs, and inserts the
        updated data into the 'sitemap' table.

        :return: None
        """
        df = pd.read_csv(self.config['SiteMapGenerationFile'])
        data_list = df[['place_id','name', 'vicinity','rating','zip_code','price_level','user_ratings_total','category']].to_dict(orient='records')
        for data in data_list:
            updated_data = self.generate_urls(data)
            self.insert_data_into_sitemap(updated_data)
        
    def generate_urls(self,data):
        """
        Generates a Google search URL based on the provided data.

        This method takes a dictionary containing place information and generates
        a Google search URL using the name and vicinity of the place.

        :param data: Dictionary containing place information.
        :return: Dictionary with an added 'url' key containing the generated Google search URL.
        """
        name = data['name'].replace(" ","+")
        location = data['vicinity'].replace(" ","+")
        google_search = f"https://www.google.com/search?q={name}+{location}"            
        data["url"] = google_search
        return data
            