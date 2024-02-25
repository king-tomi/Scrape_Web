# Running the FastAPI Server

This guide will walk you through running the FastAPI server that serves a scraping endpoint.

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Install FastAPI and uvicorn:

   ```pip install fastapi uvicorn```

2. Download and extract Chromedriver for your system
    ```https://chromedriver.chromium.org/downloads```

3. Run the app:

    ```uvicorn main:app --reload```

## Example Usage

To scrape a website, send a POST request to `http://localhost:8000/scrape` with a JSON body containing the URL of the website you want to scrape:

### Request Body

``` json
    {
    "url": "https://example.com"
    }
```

### Send a request

``` bash
    curl -X 'POST' \
    'http://localhost:8000/scrape' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "url": "https://example.com"
    }'
```

### Example Response

``` json
    {
        "title": "string",
        "logo": "string",
        "colors": "list"
    }
```
