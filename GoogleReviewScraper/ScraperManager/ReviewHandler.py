import re
import traceback
import csv
import pandas as pd
from bs4 import BeautifulSoup
import traceback

class ReviewHandler:
    
    def __init__(self, time_stopper, sitemap_data):
        """
        Initializes the ReviewHandler object.

        :param time_stopper: The time constraint for reviews.
        :param sitemap_data: Data associated with the sitemap.
        """
        self.time_stopper = time_stopper
        self.review_container_store = []
        self.sitemap_data = sitemap_data

    def parse_review_data(self, review):
        """
        Parses review data and updates it with sitemap information.

        :param review: WebElement containing review data.
        :return: Parsed review data.
        """
        parsed_review = self.parse_review(review)
        if parsed_review:
            parsed_review.update(self.sitemap_data)
            return parsed_review
        
        return False
          
    def clean_data(self):
        """
        Cleans the data by removing duplicate reviews.
        """
        parsed_results_df = pd.DataFrame(self.review_container_store)
        unique_reviews_dicts = parsed_results_df.drop_duplicates()
        unique_reviews_dicts = unique_reviews_dicts.to_dict(orient='records')
            
        self.review_container_store = unique_reviews_dicts
            
    def save_data(self):
        """
        Saves parsed review data to a CSV file.
        """
        for parsed_review in self.review_container_store:
            csv_file_path = './5Zip_complete_run.csv'
            is_empty = False
            try:
                with open(csv_file_path, 'r') as csv_file:
                    is_empty = csv_file.readline() == ''
            except FileNotFoundError:
                is_empty = True 
            
            with open(csv_file_path, 'a', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=parsed_review.keys())
                
                # Write the header row if the file is empty
                if is_empty:
                    csv_writer.writeheader()
                
                # Append the data
                csv_writer.writerow(parsed_review)     
             
    def parse_review(self, review):
        """
        Parses the HTML content of a review WebElement.

        :param review: WebElement containing review data.
        :return: Parsed review data.
        """
        review_html = review.get_attribute("innerHTML")
        soup = BeautifulSoup(review_html, 'html.parser')
        try:
            review_content = soup.find(attrs={"jscontroller": "MZnM8e"})
            expand_review = review_content.find("a", class_="review-more-link")
            if expand_review:
                aria_expanded = expand_review.get('aria-expanded')
                if aria_expanded.lower() == "true":
                    review_data = review_content.get_text()
                else:
                    return False
            else:
                review_data = review_content.get_text()
        except Exception as e:
            print(e)
            return False

        try:
            time = soup.find('span', class_='dehysf')
            time_content = time.get_text()
        except Exception as e:
            time_content = None
            pass

        try:
            diner_info = soup.find('div', class_='PV7e7')
            diner_info_content = diner_info.get_text()
            diner_info_content = diner_info_content.replace("\xa0", "")
        except Exception as e:
            diner_info_content = None
            pass

        try:
            extra_information = soup.find('div', class_='k8MTF')
            extra_information_content = extra_information.get_text()
        except Exception as e:
            extra_information_content = None
            pass
        
        parsed_results = {
            "review": review_data,
            "time": time_content,
            "diner_info": diner_info_content,
            "extra_info": extra_information_content
        }

        if self.check_review_constraints(parsed_results):
            return parsed_results

        return False
    
    def append_parsed_reviews(self, parsed_review):
        """
        Appends parsed review data to the container store.

        :param parsed_review: Parsed review data.
        """
        self.review_container_store.append(parsed_review)
    
    def check_if_duplicates(self, parsed_review):
        """
        Checks if the parsed review is a duplicate.

        :param parsed_review: Parsed review data.
        :return: True if duplicate, False otherwise.
        """
        try:
            set_of_frozen_sets = {frozenset(d.items()) for d in self.review_container_store}
            new_frozen_set = frozenset(parsed_review.items())
            
            if new_frozen_set in set_of_frozen_sets:
                return True
            else:
                set_of_frozen_sets.add(new_frozen_set)
                return False
        except Exception as e:
            traceback.print_exc()
            print(e)
        
    def hit_time_constraints(self, parsed_results):
        """
        Checks if the review hits the specified time constraints.

        :param parsed_results: Parsed review data.
        :return: True if time constraints are met, False otherwise.
        """
        time_pattern = r"(\d+)\s+(hours|days|years|months)\s+ago"
        
        matches = re.search(time_pattern, parsed_results['time'])
        
        if matches:
            number, unit = matches.groups()
            if unit == "years" and int(number) >= self.time_stopper:
                return True
        return False

    def check_review_constraints(self, parsed_results):       
        """
        Checks if the parsed review data meets certain constraints.

        :param parsed_results: Parsed review data.
        :return: True if constraints are met, False otherwise.
        """
        if parsed_results['review'] in [None, ''] and parsed_results['diner_info'] is None:
            return False
        return True
    
    def test_link_click(self, more_data):
        """
        Tests link click and prints full review content.

        :param more_data: WebElement containing additional review data.
        """
        inner_html = more_data.get_attribute("innerHTML")
