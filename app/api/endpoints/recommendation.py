import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.environ.get("MONGO_URI")
client = AsyncIOMotorClient(str(os.getenv("MONGODB_URL")))
db = client.get_database("bring_the_menu_db")
collection = db.get_collection("restaurant_info2")

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
    
    if search_term not in vectorizer.get_feature_names():
        return []

    idx = vectorizer.get_feature_names().index(search_term)
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Enhance scores with the weights of ratings
    for i in range(len(sim_scores)):
        sim_scores[i] = (sim_scores[i][0], sim_scores[i][1] * float(df.iloc[i]['rating']))
    
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:3]  # Get the top 2 recommendations
    food_indices = [i[0] for i in sim_scores]
    
    return df.iloc[food_indices].to_dict('records')
