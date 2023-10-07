from motor.motor_asyncio import AsyncIOMotorClient
import os
from bson import ObjectId

MONGO_URI = os.environ.get("MONGO_URI")
client = AsyncIOMotorClient(str(os.getenv("MONGODB_URL")))
db = client.get_database("bring_the_menu_db") 
restaurant_info_collection = db.get_collection("restaurant_info6")
food_category_search_collection = db.get_collection("food_category_search")

async def get_restaurants_by_location(location: str):
    #data table name messed up...
    cursor = restaurant_info_collection.find({"Neighboring University": {"$regex": "Geroge", "$options": 'i'}})
    restaurants = await cursor.to_list(length=1000)  # adjust the length as needed
    
    unique_restaurants = []
    seen = set()
    
    for restaurant in restaurants:
        identifier = (restaurant['name'], restaurant['address'])
        if identifier not in seen:
            seen.add(identifier)
            restaurant["_id"] = str(restaurant["_id"])
            unique_restaurants.append(restaurant)

    return unique_restaurants

async def get_restaurants_by_category(category: str):
    cursor = restaurant_info_collection.find({"categories": {"$regex": category, "$options": 'i'}})
    restaurants = await cursor.to_list(length=100)
    
    unique_restaurants = []
    seen = set()

    for restaurant in restaurants:
        identifier = (restaurant['name'], restaurant['address'])
        if identifier not in seen:
            seen.add(identifier)
            restaurant["_id"] = str(restaurant["_id"])
            unique_restaurants.append(restaurant)

    return unique_restaurants