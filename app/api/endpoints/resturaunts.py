from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import requests
import os
from api.helpers import resturaunts_helper
from api.helpers import database_helper

router = APIRouter()


@router.get("/add_restaurants_to_table/{location}")
async def read_restaurants(location: str):
    restaurants = resturaunts_helper.get_restaurants(location)
    if not restaurants:
        raise HTTPException(status_code=404, detail="Restaurants not found")
    return restaurants


@router.get("/add_restaurants_by_category_to_table/{category}")
async def read_restaurants(category: str):
    restaurants = resturaunts_helper.get_restaurants_by_category(category)
    if not restaurants:
        raise HTTPException(status_code=404, detail="Restaurants not found")
    return restaurants

@router.get("/restaurants/{location}")
async def read_restaurants(location: str):
    restaurants = await database_helper.get_restaurants_by_location(location)
    if not restaurants:
        raise HTTPException(status_code=404, detail="Restaurants not found")
    return restaurants

@router.get("/restaurants_by_category/{category}")
async def read_restaurants_by_category(category: str):
    restaurants = await database_helper.get_restaurants_by_category(category)
    if not restaurants:
        raise HTTPException(status_code=404, detail="Restaurants not found")
    return restaurants