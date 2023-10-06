# import motor.motor_asyncio
# from decouple import Config
# # import os
# # print(os.getcwd())

# # config = Config("../.env")
# # MONGODB_URL = config.get("MONGODB_URL")
# MONGODB_URL = "mongodb+srv://patriothacks2023:<1b7e236beb>@patriothacks2023.vggoylp.mongodb.net/?retryWrites=true&w=majority"

# client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)

# database = client.patriothacks  # Use your actual Database name here
# collection = database.get_collection("test")  # Use your actual Collection name here

import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DataBase:
    client: AsyncIOMotorClient = None

database = DataBase()

async def get_database() -> AsyncIOMotorClient:
    return database.client

async def connect_to_mongo():
    database.client = AsyncIOMotorClient(str(os.getenv("MONGODB_URL")))
    
    # Ping the database to ensure a successful connection
    db = database.client.get_database("sample_airbnb") #test is a name of 
    await db.command("ping")
    print("Connected to MongoDB \n")

    collection = db.get_collection("listingsAndReviews") 
    # documents = await collection.find().to_list(length=2)  # Adjust the length as needed
    # for doc in documents:
    #     print(doc)
    documents = await collection.find({}, {"name": 1, "_id": 0}).to_list(length=10)  # Adjust the length as needed
    for doc in documents:
        print(doc['name'])

async def close_mongo_connection():
    database.client.close()
    print("Connection to MongoDB closed")
