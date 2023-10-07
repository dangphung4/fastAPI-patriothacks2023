import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import MinMaxScaler
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter, HTTPException, Depends
import os
from dotenv import load_dotenv

MONGO_URI = os.environ.get("MONGO_URI")
client = AsyncIOMotorClient(str(os.getenv("MONGODB_URL")))
db = client.get_database("bring_the_menu_db")
collection = db.get_collection("restaurant_info6")

router = APIRouter()

async def fetch_data():
    cursor = collection.find({})
    data = await cursor.to_list(length=1000)
    return pd.DataFrame(data)


async def get_recommendations(restaurant_name: str):
    df = await fetch_data()
    df['all_categories'] = df['categories'].apply(', '.join)
    
    vectorizer = TfidfVectorizer(analyzer='word', stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['all_categories'])
    
    knn = NearestNeighbors(n_neighbors=6, metric='cosine')  
    knn.fit(tfidf_matrix)
    
    if not any(df['name'].str.contains(restaurant_name, case=False, na=False)):
        return []

    matched_restaurants = df[df['name'].str.contains(restaurant_name, case=False, na=False)]

    restaurant_idx = matched_restaurants.index[0]
    restaurant_vector = tfidf_matrix[restaurant_idx]
    distances, indices = knn.kneighbors(restaurant_vector)

    # Collect 6 recommendations including the input restaurant
    recommended_restaurants = df.iloc[indices[0]].to_dict('records')

    # Filter out the input restaurant from recommendations
    final_recommendations = [restaurant for restaurant in recommended_restaurants 
                             if restaurant['name'].lower() != restaurant_name.lower()]

    # If more than one restaurant has the same name, ensure that 5 unique recommendations are returned
    if len(final_recommendations) > 5:
        final_recommendations = final_recommendations[:5]

    return [dict(item, _id=str(item['_id'])) for item in final_recommendations]

# Example usage



@router.get("/recommendations/{search_term}")
async def read_recommendations(search_term: str):
    recommendations = await get_recommendations(search_term)
    if not recommendations:
        raise HTTPException(status_code=404, detail=f"No recommendations found for {search_term}")
    return recommendations