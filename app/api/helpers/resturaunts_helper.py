from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from bson import json_util
import json
import requests
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


from bs4 import BeautifulSoup
import urllib.parse  
from urllib.parse import quote

YELP_API_KEY = os.environ.get("YELP_API_KEY")
MONGO_URI = os.environ.get("MONGO_URI")
DIFFBOT_TOKEN = os.environ.get("DIFFBOT_TOKEN")

client = AsyncIOMotorClient(str(os.getenv("MONGODB_URL")))
db = client.get_database("bring_the_menu_db") 
searches_collection = db.get_collection("searches")
restaurant_info_collection = db.get_collection("restaurant_info")



# Yelp API endpoint
YELP_API_ENDPOINT = "https://api.yelp.com/v3/businesses/search"
def get_restaurants(location):
    """
    Get a list of restaurants based on the given location, including their names and coordinates.
    """
    headers = {
        "Authorization": f"Bearer {YELP_API_KEY}"
    }
    params = {
        "term": "restaurants",
        "location": location,
        "limit": 1,  # Adjust the limit as needed
        "radius": 8047 # 5 mile radius
    }

    response = requests.get(YELP_API_ENDPOINT, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return []

    data = response.json()
    businesses = data.get("businesses", [])

    restaurants = []

     # Create a new Selenium browser instance
    options = Options()
    options.add_argument("--headless")  # Run browser in headless mode (no GUI)
    browser = webdriver.Chrome(options=options)

    for business in businesses:
        
        # Fetch the Yelp page of the restaurant to scrape the official website
        yelp_url = business['url']
        yelp_page_content = requests.get(yelp_url).content
        soup = BeautifulSoup(yelp_page_content, 'lxml')

         # Scrape the official website URL from the Yelp page
        official_site_url = None
        website_link = soup.find('a', href=True, rel='noopener')
        if website_link:
            official_site_url = website_link['href']

        # If the official website URL is found, scrape it for deals/specials
        deals = []
        specials = []
        if official_site_url:
            parsed = urllib.parse.urlparse(official_site_url)
            actual_url = urllib.parse.parse_qs(parsed.query)['url'][0]
            print(f"Actual site URL: {actual_url}")

            browser.get(actual_url)  # Selenium loads the webpage
            
            try:
                # Adjust the expected_conditions and timeout as needed
                element_present = EC.presence_of_element_located((By.ID, 'menu-item'))
                WebDriverWait(browser, 30).until(element_present)
            except TimeoutException:
                print("Timed out waiting for page to load")

            soup_specials = BeautifulSoup(browser.page_source, 'lxml')
            print(f"Specials Page Content: {soup_specials.prettify()[:500]}")  

            
              # Extracting deals
            deals_elements = soup_specials.find_all('div', class_='deals')
            print(f"Found {len(deals_elements)} deals elements.")  # Print the count of found elements
            
            for deal in deals_elements:
                deals.append(deal.text.strip())

            # Extracting specials
            specials_elements = soup_specials.find_all('div', class_='specials')
            print(f"Found {len(specials_elements)} specials elements.")
            
            for special in specials_elements:
                specials.append(special.text.strip())
        info = {
            "name": business['name'],
            "coordinates": business['coordinates'],
            "address": " ".join(business['location']['display_address']),
            "rating": business['rating'],
            "price": business.get('price', "Not available"),  # Handling cases where price info might not be available
            "categories": [category['title'] for category in business['categories']],
            "image_url": business['image_url'],
            "phone": business['phone'],
            "distance": business['distance'],
            "yelp_url": yelp_url,
            "yelp_url": yelp_url,
            "official_site_url": official_site_url,
            "deals": deals,  # Store the scraped deals/specials
            "specials": specials
            
        }
        restaurants.append(info)

        # Store the information in MongoDB Atlas
        restaurant_info_collection.insert_one(info)

    browser.quit()
    search_data = {"location": location, "results": len(restaurants)}
    searches_collection.insert_one(search_data)

    restaurants_json = json.loads(json_util.dumps(restaurants))
    return restaurants_json

