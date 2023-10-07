import pandas as pd
from gensim.models import KeyedVectors
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter, HTTPException, Depends
import os
import gensim.downloader as api

# info = api.info()  # show info about available models/datasets
model = api.load("word2vec-google-news-300")

# Load the pre-trained Word2Vec model
# word_vectors = KeyedVectors.load_word2vec_format('path/to/your/pretrained/model.bin', binary=True)

MONGO_URI = os.environ.get("MONGO_URI")
client = AsyncIOMotorClient(str(os.getenv("MONGODB_URL")))
db = client.get_database("bring_the_menu_db")
collection = db.get_collection("restaurant_info6")

router = APIRouter()

async def fetch_data():
    cursor = collection.find({})
    data = await cursor.to_list(length=1000)
    return pd.DataFrame(data)
async def get_recommendations(search_term: str):
    df = await fetch_data()

    if search_term not in model.key_to_index:
        return []

    # Get the unique categories from your MongoDB collection
    unique_categories = df['categories'].explode().unique()

    # Compute word similarities using Word2Vec model for categories that exist in your collection
    word_similarities = []
    for category in unique_categories:
        if category in model.key_to_index:
            similarities = model.most_similar(category, topn=10)
            word_similarities.extend(similarities)

    # Sort the word similarities by similarity score
    word_similarities.sort(key=lambda x: x[1], reverse=True)

    # Filter the dataframe based on word similarities
    similar_categories = [category for category, _ in word_similarities if category in unique_categories]
    filtered_df = df[df['categories'].str.contains('|'.join(similar_categories), case=False, na=False)]

    # Sort the filtered dataframe by rating and return top recommendations
    filtered_df = filtered_df.sort_values(by='rating', ascending=False)
    recommendations = filtered_df.head(3)

    return [dict(item, _id=str(item['_id'])) for item in recommendations.to_dict('records')]



@router.get("/recommendations/{search_term}")
async def read_recommendations(search_term: str):
    recommendations = await get_recommendations(search_term)
    if not recommendations:
        raise HTTPException(status_code=404, detail=f"No recommendations found for {search_term}")
    return recommendations