from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from bson import json_util
import json
import requests
import os
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
        "limit": 5,  # Adjust the limit as needed
        "radius": 8047 # 5 mile radius
    }

    response = requests.get(YELP_API_ENDPOINT, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return []

    data = response.json()
    businesses = data.get("businesses", [])

    restaurants = []
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
        if official_site_url:
            parsed = urllib.parse.urlparse(official_site_url)
            actual_url = urllib.parse.parse_qs(parsed.query)['url'][0]
            print(f"Actual site URL: {actual_url}")


            encoded_url = quote(official_site_url, safe='')  # URL-encode the official site URL
            diffbot_url = f'https://api.diffbot.com/v3/article?token={DIFFBOT_TOKEN}&url={encoded_url}'
            diffbot_response = requests.get(diffbot_url)
            print(f"Diffbot raw response: {diffbot_response.text}")  
            
            if diffbot_response.status_code != 200:
                print(f"Error fetching page: {diffbot_response.text}")  # Print the error for review
                continue  # Skip to the next iteration if there's an error
            diffbot_data = json.loads(diffbot_response.text)
            deals = diffbot_data.get('objects', [{}])[0].get('text', '').split('\n')
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
            "deals": deals  # Store the scraped deals/specials
            
        }
        restaurants.append(info)

        # Store the information in MongoDB Atlas
        restaurant_info_collection.insert_one(info)
    
    search_data = {"location": location, "results": len(restaurants)}
    searches_collection.insert_one(search_data)

    restaurants_json = json.loads(json_util.dumps(restaurants))
    return restaurants_json

