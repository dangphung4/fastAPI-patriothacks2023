from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorClient
from bson import json_util
import json
import requests
import os

from bson import json_util
import json

from bs4 import BeautifulSoup
import urllib.parse  
from urllib.parse import quote

YELP_API_KEY = os.environ.get("YELP_API_KEY")
MONGO_URI = os.environ.get("MONGO_URI")


client = AsyncIOMotorClient(str(os.getenv("MONGODB_URL")))
db = client.get_database("bring_the_menu_db") 
searches_collection = db.get_collection("searches")
restaurant_info_collection = db.get_collection("restaurant_info6")
category_search_collection = db.get_collection("food_category_search")

# Yelp API endpoint
YELP_API_ENDPOINT = "https://api.yelp.com/v3/businesses/search"
def get_restaurants(location):
    
    """
    Get a list of restaurants based on the given location, including their names and coordinates.
    """
    search_terms = [
        'restaurants', 'boba stores', 'cafes', 'food trucks', 'bakery', 'bar',
        'brewery', 'buffet', 'cafeteria', 'coffee shop', 'deli', 'dessert shop',
        'diner', 'fast food', 'food court', 'gastropub', 'ice cream shop',
        'juice bar', 'pizzeria', 'pub', 'seafood market', 'steakhouse', 'sushi bar',
        'tea house', 'winery', 'bagel shop', 'boba shop', 'brasserie', 'breakfast spot',
        'bistro', 'burrito place', 'candy store', 'cheese shop', 'chicken joint',
        'chocolatier', 'cupcake shop', 'donut shop', 'fish and chips shop',
        'food truck', 'fried chicken joint', 'gelato shop', 'grill', 'hotdog joint',
        'pancake house', 'pastry shop', 'pie shop', 'salad place', 'sandwich shop',
        'smoothie shop', 'soup place', 'taco stand', 'tapas restaurant', 'waffle house',
        'vegan restaurant', 'vegetarian restaurant'
    ] 
    for term in search_terms:
        headers = {
            "Authorization": f"Bearer {YELP_API_KEY}"
        }
        params = {
            "term": term,
            "location": location,
            "limit": 50,  # Adjust the limit as needed
            "radius": 8047 
        }

        response = requests.get(YELP_API_ENDPOINT, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Failed to retrieve data for {term}: {response.status_code}")
            continue

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
            actual_url = None 
            website_link = soup.find('a', href=True, rel='noopener')
            if website_link:
                official_site_url = website_link['href']

            # If the official website URL is found, scrape it for deals/specials
            deals = []
            specials = []
            if official_site_url:
                parsed = urllib.parse.urlparse(official_site_url)
                if 'url' in urllib.parse.parse_qs(parsed.query):
                    actual_url = urllib.parse.parse_qs(parsed.query)['url'][0]
                    print(f"Actual site URL: {actual_url}")
                else:
                    actual_url = official_site_url 
                    
            info = {
                "name": business['name'],
                "coordinates": business['coordinates'],
                "Neighboring University" : location,
                "address": " ".join(business['location']['display_address']),
                "rating": business['rating'],
                "price": business.get('price', "Not available"),  # Handling cases where price info might not be available
                "categories": [category['title'] for category in business['categories']],
                "image_url": business['image_url'],
                "phone": business['phone'],
                "distance": business['distance'],
                "official_site_url": actual_url,
                
                # Add more fields if needed
            }
            restaurants.append(info)
            restaurant_info_collection.insert_one(info)
    
    search_data = {"location": location, "results": len(restaurants)}
    searches_collection.insert_one(search_data)

    return restaurants

def get_restaurants_by_category(
    category: str,
):
    """
    Get a list of restaurants based on the specified category or theme and location.
    """
    headers = {
        "Authorization": f"Bearer {YELP_API_KEY}"
    }
    params = {
        "term": category,  # Use the specified category as the search term
        "location": "George Mason University", # this should be location later
        "limit": 10,  # Adjust the limit as needed
        "radius": 8047 
    }

    response = requests.get(YELP_API_ENDPOINT, headers=headers, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve data: {response.status_code}")

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
        specials = []
        if official_site_url:
            parsed = urllib.parse.urlparse(official_site_url)
            actual_url = urllib.parse.parse_qs(parsed.query)['url'][0]

        info = {
            "name": business['name'],
            "coordinates": business['coordinates'],
            "address": " ".join(business['location']['display_address']),
            "rating": business['rating'],
            "price": business.get('price', "Not available"),
            "categories": [category['title'] for category in business['categories']],
            "image_url": business['image_url'],
            "phone": business['phone'],
            "distance": business['distance'],
            "official_site_url": actual_url,
        }
        restaurants.append(info)
        info_dict = dict(info)

        restaurants.append(info_dict)

    # Insert the plain dictionary into the collection
        # restaurant_info_collection.insert_one(info_dict)
    
    search_data = {"location": "George Mason University", "results": len(restaurants), "category": category}
    # category_search_collection.insert_one(search_data)
        
    return restaurants