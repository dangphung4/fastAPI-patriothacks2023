from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from database import connect_to_mongo, close_mongo_connection
from api.endpoints import resturaunts
from api.endpoints import recommendation

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

origins = ["http://127.0.0.1:8000/", "http://localhost:5173", "http://127.0.0.1:5173/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(resturaunts.router)
app.include_router(recommendation.router)

@app.get("/")
def root():
    return {"message": "Server is running"}

