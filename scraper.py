import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
import os

BASE_DIR = os.getcwd()
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

        #Extract text
        text = soup.get_text()

        result = {"title": title, "logo": logo, "colors": list(colors), "text": text}

    except Exception as e:
        print(f"Failed to scrape the website using requests and BeautifulSoup")

    if result != {} and result['title'] is not None:
        return result
    else:
        # If scraping fails, try using Selenium
        try:
            # Set up the Chrome driver
            colors = set()
            service = Service(f"{BASE_DIR}/chromedriver")
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run headless to avoid opening a browser window
            driver = webdriver.Chrome(service=service, options=chrome_options)

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
            text = ' '.join(element.text for element in text_elements)

            driver.quit()  # Close the browser

            return {"title": title, "logo": logo, "colors": list(colors), "text": text}

        except Exception as e:
            print(f"Failed to scrape the website using Selenium: {e}")
