from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import requests
import os

YELP_API_KEY = os.environ.get("YELP_API_KEY")

MONGO_URI = os.environ.get("MONGO_URI")
client = AsyncIOMotorClient(str(os.getenv("MONGODB_URL")))
db = client.get_database("bring_the_menu_db") 
searches_collection = db.get_collection("searches")

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
        "limit": 20,  # Adjust the limit as needed
        "radius": 8047 
    }

    response = requests.get(YELP_API_ENDPOINT, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return []

    data = response.json()
    businesses = data.get("businesses", [])

    restaurants = []
    for business in businesses:
        info = {
            "name": business['name'],
            "coordinates": business['coordinates'],
            "address": " ".join(business['location']['display_address']),
            "rating": business['rating'],
            "price": business.get('price', "Not available"),  # Handling cases where price info might not be available
            "categories": [category['title'] for category in business['categories']],
            "image_url": business['image_url'],
            "phone": business['phone'],
            "distance": business['distance']
            # Add more fields if needed
        }
        restaurants.append(info)
    
    search_data = {"location": location, "results": len(restaurants)}
    searches_collection.insert_one(search_data)

    return restaurants
