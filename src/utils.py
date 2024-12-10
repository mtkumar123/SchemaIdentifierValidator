from src.config import get_settings
from contextlib import asynccontextmanager
from typing import AsyncIterator, Annotated
from pymongo import MongoClient, database
from fastapi import FastAPI, Depends, Header
import os

settings = get_settings()
mongo_client: MongoClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global mongo_client
    mongo_client = MongoClient(
        host=settings.mongo_db_url,
        port=settings.mongo_db_port,
    )
    os.makedirs(settings.upload_file_location, exist_ok=True)
    yield
    mongo_client.close()


def get_database() -> database.Database:
    return mongo_client[settings.db_name]


def valid_content_length(content_length: int = Header(...)):
    return content_length


MongoClientDep = Annotated[database.Database, Depends(get_database)]
