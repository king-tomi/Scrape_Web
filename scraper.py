from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import re
import os

def retry_on_stale_element(func):
    def wrapper(*args, **kwargs):
        retries = 3
        while retries > 0:
            try:
                return func(*args, **kwargs)
            except StaleElementReferenceException:
                retries -= 1
        raise StaleElementReferenceException("Max retries exceeded for stale element")
    return wrapper

class BasePage:
    def __init__(self, driver):
        self.driver = driver

class HomePage(BasePage):
    def __init__(self, driver, url):
        super().__init__(driver)
        self.url = url

    def navigate_to_home_page(self):
        self.driver.get(self.url)

class ResultsPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.logo_element = (By.XPATH, '//link[@rel="icon" or @rel="shortcut icon"]')
        self.colors_elements = (By.TAG_NAME, 'style')
        self.text_elements = (By.XPATH, '//*[not(self::script or self::style)]')

    @retry_on_stale_element
    def get_title(self):
        return self.driver.title

    @retry_on_stale_element
    def get_logo_url(self):
        logo_element = self.driver.find_elements(*self.logo_element)
        return logo_element[0].get_attribute("href") if logo_element else ""

    @retry_on_stale_element
    def get_colors(self):
        colors = set()

        # Extract colors from <style> tags
        style_tags = self.driver.find_elements(By.TAG_NAME, "style")
        for style_tag in style_tags:
            styles = style_tag.get_attribute("innerHTML")
            if styles:
                hex_colors = re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}", styles)
                colors.update(hex_colors)

        # Extract colors from inline styles in HTML elements
        elements_with_style = self.driver.find_elements(By.XPATH, '//*[contains(@style, "color")]')
        for element in elements_with_style:
            style_attribute = element.get_attribute("style")
            if style_attribute:
                inline_hex_colors = re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}", style_attribute)
                colors.update(inline_hex_colors)
        return list(colors)

    @retry_on_stale_element
    def get_text(self):
        text_elements = self.driver.find_elements(*self.text_elements)
        return ' '.join(element.text.replace("\n", "") for element in text_elements)

BASE_DIR = os.getcwd()

@retry_on_stale_element
def scrape_website(url):
    """
    Scrape the specified website and return the title, logo URL, and colors.

    Args:
        url_request (URLRequest): The URL of the website to scrape.

    Returns:
        dict: A dictionary containing the title, logo URL, and colors of the website.
    """

    # Try scraping the website using requests and BeautifulSoup
    result = {}
    try:
        # Fetch the webpage
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to fetch the webpage")

        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract the title
        title = soup.title.string if soup.title else ""

        # Extract the logo URL
        logo = ""
        for link in soup.find_all("link", rel="icon"):
            if link.has_attr("href"):
                logo = link["href"]
                break

        # Extract colors from CSS styles
        colors = set()
        style_tags = soup.find_all("style")
        for style_tag in style_tags:
            styles = style_tag.string
            if styles:
                hex_colors = re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}", styles)
                colors.update(hex_colors)

        # Extract colors from inline styles in HTML elements
        elements_with_style = soup.find_all(lambda tag: tag.has_attr('style') and 'color' in tag['style'])
        for element in elements_with_style:
            style_attribute = element['style']
            if style_attribute:
                inline_hex_colors = re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}", style_attribute)
                colors.update(inline_hex_colors)

        #Extract text
        text = soup.get_text().replace("\n", "")

        result = {"title": title, "logo": logo, "colors": list(colors), "text": text}

    except Exception as e:
        print(f"Failed to scrape the website using requests and BeautifulSoup")

    if result != {} and result['title'] is not None and len(result['text']) > 1000:
        return result
    else:
        # If scraping fails, try using Selenium
        print("BS4 did not work, trying selenium")
        try:
            # Set up the Chrome driver
            result = {}
            colors = set()
            service = Service(f"{BASE_DIR}/chromedriver")
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run headless to avoid opening a browser window
            chrome_options.add_argument("--disable-gpu")
            driver = webdriver.Chrome(service=service, options=chrome_options)

            home_page = HomePage(driver, url)
            home_page.navigate_to_home_page()

            results_page = ResultsPage(driver)
            title = results_page.get_title()
            logo = results_page.get_logo_url()
            colors = results_page.get_colors()
            text = results_page.get_text()

            result = {"title": title, "logo": logo, "colors": list(colors), "text": text}
            if result['title'] != "":
                return result
            else:
                # Load the webpage
                driver.get(url)

                # Extract the title
                title = driver.title

                # Extract the logo URL
                logo = ""
                elements = driver.find_elements(By.XPATH, '//link[@rel="icon" or @rel="shortcut icon"]')
                if elements:
                    logo = elements[0].get_attribute("href")

                # Extract colors from <style> tags
                style_tags = driver.find_elements(By.TAG_NAME, "style")
                for style_tag in style_tags:
                    styles = style_tag.get_attribute("innerHTML")
                    if styles:
                        hex_colors = re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}", styles)
                        colors.update(hex_colors)

                # Extract colors from inline styles in HTML elements
                elements_with_style = driver.find_elements(By.XPATH, '//*[contains(@style, "color")]')
                for element in elements_with_style:
                    style_attribute = element.get_attribute("style")
                    if style_attribute:
                        inline_hex_colors = re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}", style_attribute)
                        colors.update(inline_hex_colors)

                # Extract the text of the website
                text_elements = driver.find_elements(By.XPATH, '//*[not(self::script or self::style)]')
                text = ' '.join(element.text.replace("\n", "") for element in text_elements)

                driver.quit()  # Close the browser

                return {"title": title, "logo": logo, "colors": list(colors), "text": text}

        except Exception as e:
            print(f"Failed to scrape the website using Selenium: {e}")
