from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import requests
import os
from api.helpers import resturaunts_helper

router = APIRouter()


@router.get("/restaurants/{location}")
async def read_restaurants(location: str):
    restaurants = resturaunts_helper.get_restaurants(location)
    if not restaurants:
        raise HTTPException(status_code=404, detail="Restaurants not found")
    return restaurants



