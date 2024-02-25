from fastapi import FastAPI
from pydantic import BaseModel
from scraper import scrape_website

# Create a FastAPI app
app = FastAPI()

# Define a request model
class URLRequest(BaseModel):
    url: str

# Define the endpoint
@app.post("/scrape")
async def scrape(url_request: URLRequest):
    """
    Scrape the specified website and return the title, logo URL, and colors.

    Args:
        url_request (URLRequest): The URL of the website to scrape.

    Returns:
        dict: A dictionary containing the title, logo URL, and colors of the website.
    """
    url = url_request.url
    data = scrape_website(url)
    return data
