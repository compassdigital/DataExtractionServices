import time
from selenium import webdriver
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
import csv
import traceback
import pandas as pd
import re
from io import StringIO
import random

from ScraperManager.ReviewHandler import ReviewHandler

class GooogleReviewScraper:
    
    def __init__(self, scrape_data, config, db):
        """
        Initializes the GooogleReviewScraper object.

        :param scrape_data: Data to be scraped.
        :param config: Configuration data.
        :param db: Database manager object.
        """
        self.review_time_stopper = config['ReviewTimeStoperYears']
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("--headless")
        options.add_argument("--enable-javascript")
        options.add_argument("window-size=1400,600")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.scrape_data = scrape_data
        self.reviewHandler = ReviewHandler(self.review_time_stopper, self.scrape_data)
        self.db = db
        self.review_container_tracker = 0
        
    def open_browser(self):
        """
        Opens the browser and navigates to the provided URL.

        :return: None
        """
        try:       
            stealth(self.driver,
                    languages=["en-US", "en"],  
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36',
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=False,
                    run_on_insecure_origins=False
            ) 
            self.driver.get(self.scrape_data['url'])
        except Exception as e: 
            self.driver.close()

    def close_browser(self):
        """
        Closes the browser.

        :return: None
        """
        self.driver.close()

    def scrape_reviews(self):
        """
        Initiates the process of scraping Google reviews.

        :return: True if successful, False otherwise.
        """
        try:
            text_to_find = "View all Google reviews"
            click_review = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text_to_find}')]"))
            )
            if click_review:
                click_review.click()
                text_of_button = "Newest"
                find_newest = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text_of_button}')]"))
                )
                if find_newest:
                    self.driver.execute_script("arguments[0].click();", find_newest)
                    self.scroll_down_reviews()
                else:
                    return False
        except Exception as e:
            return False

    def scroll_down_reviews(self):
        """
        Scrolls down to load more reviews and parses them.

        :return: None
        """
        try:
            scroll_element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="gsr"]/span[2]/g-lightbox/div/div[2]/div[3]/span/div/div/div/div[2]'))
            )
            
            if scroll_element:
                while True:
                    time.sleep(1)
                    self.find_more_review_button()
                    scroll_distance = 100  # Adjust this value to scroll by your desired distance in pixels
                    self.driver.execute_script("arguments[0].scrollBy(0, arguments[1]);", scroll_element, scroll_distance)
                    collected_reviews = self.find_review_container()
                    time.sleep(1)  
                    for review in collected_reviews:
                        parsed_review = self.reviewHandler.parse_review_data(review)
                        if parsed_review:
                            if self.reviewHandler.hit_time_constraints(parsed_review):
                                break
                            else:
                                self.db.insert_review(parsed_review)
                    if self.check_bottom_of_the_page(scroll_element):
                        break  
        except Exception as e:
            self.reviewHandler.save_data()
            return False

    def find_more_review_button(self):
        """
        Finds and clicks the "More" button to expand reviews.

        :return: None
        """
        try:
            review_container = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="reviewSort"]/div'))
            )
            if review_container:
                nested_element = review_container.find_elements(By.CLASS_NAME, "review-more-link")

                if nested_element:
                    for ele in nested_element:
                        aria_expanded = ele.get_attribute('aria-expanded')
                        if aria_expanded == 'false':
                            is_in_view = self.check_element_in_view(ele)
                            if is_in_view:
                                ele.click()  
        except Exception as e:
            return

    def check_element_in_view(self, ele):
        """
        Checks if an element is in the view.

        :param ele: WebElement to check.
        :return: True if the element is in view, False otherwise.
        """
        if "review-more-link" in ele.get_attribute("class"):
            is_in_view = self.driver.execute_script(
                "var elem = arguments[0], box = elem.getBoundingClientRect(), cx = box.left + box.width / 2, cy = box.top + box.height / 2, e = document.elementFromPoint(cx, cy); for (; e; e = e.parentElement) { if (e === elem) return true; } return false;",
                ele
            )
            return is_in_view

    def find_review_container(self):
        """
        Finds and returns the updated review container.

        :return: List of WebElement containing reviews.
        """
        review_container = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="reviewSort"]/div'))
        )
        
        if review_container:   
            js_code = f"return document.querySelectorAll('[jscontroller=fIQYlf]');"
            updated_containers = self.driver.execute_script(js_code)
            
            if len(updated_containers) >= 100:
                updated_containers = self.remove_already_checked_reviews(updated_containers)
            return updated_containers

    def remove_already_checked_reviews(self, updated_containers):
        """
        Removes already checked reviews from the list.

        :param updated_containers: List of reviews.
        :return: Updated list of reviews.
        """
        # Calculate the index for the midpoint
        midpoint = len(updated_containers) // 2

        # Slice the array from the midpoint to the end
        result = updated_containers[midpoint:]

        return result

    def check_bottom_of_the_page(self, scroll_element):
        """
        Checks if the bottom of the page is reached.

        :param scroll_element: The scrollable element.
        :return: True if the bottom is reached, False otherwise.
        """
        script = """
            var element = arguments[0];
            return {
                scrollHeight: element.scrollHeight,
                scrollTop: element.scrollTop,
                clientHeight: element.clientHeight
            };
            """

        # Assuming 'self.driver' is your Selenium WebDriver instance and 'scroll_element' is the scrollable element
        scroll_properties = self.driver.execute_script(script, scroll_element)

        module_height =  int(scroll_properties['scrollHeight'])
        scrolled_distance =  int(scroll_properties['scrollTop'])
        client_height = int(scroll_properties['clientHeight'])
        
        total_height = scrolled_distance + client_height
        
        if abs(total_height - module_height) <= 10:
            return True
        return False
