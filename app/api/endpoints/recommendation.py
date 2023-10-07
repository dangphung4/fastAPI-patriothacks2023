import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter, HTTPException, Depends
import os
from dotenv import load_dotenv

MONGO_URI = os.environ.get("MONGO_URI")
client = AsyncIOMotorClient(str(os.getenv("MONGODB_URL")))
db = client.get_database("bring_the_menu_db")
collection = db.get_collection("restaurant_info2")

router = APIRouter()

async def fetch_data():
    cursor = collection.find({})
    data = await cursor.to_list(length=1000)
    return pd.DataFrame(data)

async def get_recommendations(search_term: str):
    df = await fetch_data()
    df['all_categories'] = df['categories'].apply(', '.join)

    vectorizer = CountVectorizer()
    count_matrix = vectorizer.fit_transform(df['all_categories'])
    cosine_sim = cosine_similarity(count_matrix)

    if search_term not in vectorizer.get_feature_names_out():
        return []

    idx = list(vectorizer.get_feature_names_out()).index(search_term)
    sim_scores = list(enumerate(cosine_sim[idx]))

    for i in range(len(sim_scores)):
        exact_match_weight = 1
        rating_weight = float(df.iloc[i]['rating']) / 5  # Normalize the rating to a scale of 0 to 1

        if search_term.lower() in df.iloc[i]['all_categories'].lower().split(', '):
            exact_match_weight = 5  # Increase the weight for exact matches
            
        sim_scores[i] = (sim_scores[i][0], sim_scores[i][1] * rating_weight * exact_match_weight)

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[:3]  
    food_indices = [i[0] for i in sim_scores]

    return [dict(item, _id=str(item['_id'])) for item in df.iloc[food_indices].to_dict('records')]


@router.get("/recommendations/{search_term}")
async def read_recommendations(search_term: str):
    recommendations = await get_recommendations(search_term)
    if not recommendations:
        raise HTTPException(status_code=404, detail=f"No recommendations found for {search_term}")
    return recommendations