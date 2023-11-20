import pandas as pd
import random
import time
import multiprocessing
import json
from ScraperManager.GoogleReviewScraper import GooogleReviewScraper
from DatabaseManager.SitemapDatabaseManager import SiteMapDabaseManager as SitemapDBManager
from DatabaseManager.ReviewDatabaseManager import ReviewsDatabaseManager as ReviewDBManager

CONFIG_PATH = "./config.json"


def main():
    # Load configuration from JSON file
    config = load_config()

    # Create and initialize sitemap database manager
    sitemap_gen_db = SitemapDBManager(config)
    sitemap_gen_db.create_sitemap_table_if_not_exists()

    # Clear sitemap table and generate sitemap data
    sitemap_gen_db.clear_sitemap_table()
    sitemap_gen_db.generate_sitemap()

    # Create and initialize review database manager
    db_results = ReviewDBManager(config)
    db_results.save_and_clear_database()

    # Run multiprocessing for scraping reviews
    multi_processing_run(config, db_results)


def multi_processing_run(config, db):
    # Run multiple processes to scrape reviews concurrently
    num_processes = config['NumberOfProcess']
    processes = []

    for _ in range(num_processes):
        process = multiprocessing.Process(target=run_process, args=(config, db,))
        processes.append(process)
        time.sleep(3)  # Optional: Add a delay between process starts
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()


def run_process(config, db):
    # Create and initialize sitemap database manager within each process
    sitemap_gen_db = SitemapDBManager(config)

    # Loop to select and scrape reviews until no more available
    while True:
        data = sitemap_gen_db.select_random_sitemap_value()

        if not data:
            break
        else:
            try:
                # Print selected data
                print(f"~Running Job {data['url']}")

                # Measure time taken to scrape reviews
                start_time = time.time()
                google_scraper = GooogleReviewScraper(data, config, db)
                google_scraper.open_browser()
                google_scraper.scrape_reviews()
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"Elapsed time for 80% reviews: {elapsed_time:.6f} seconds")

                # Update the job status to 'FINISH' in the sitemap table
                sitemap_gen_db.update_finished_job(data['id'])

            except Exception as e:
                # Handle any exceptions during the scraping process
                print(e)
                print("Job failed; back into the pool it goes")
                sitemap_gen_db.update_failed_job(data['id'])


def load_sitemap(sitemap_path):
    # Load sitemap data from CSV file and convert to dictionary
    df = pd.read_csv(sitemap_path)
    sitemap = df.to_dict(orient='records')
    return sitemap


def load_config():
    # Load configuration data from JSON file
    with open(CONFIG_PATH, 'r') as file:
        config_data = json.load(file)
    return config_data


#NOTE TESTING ONLY
def run_single_test(sitemap, config, db):
    # Shuffle the sitemap for random testing
    random.shuffle(sitemap)

    # Loop to run a single test (scrape reviews for one data point)
    for data in sitemap:
        google_scraper = GooogleReviewScraper(data, config, db)
        google_scraper.open_browser()
        checker = google_scraper.scrape_reviews()

        if checker is False:
            # Handle case where scraping fails; can add it back to the pool
            pass

        # Exit after the first iteration (for demonstration purposes)
        break


# Entry point of the script
if __name__ == "__main__":
    main()
