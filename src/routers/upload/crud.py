from pymongo.database import Database
from src.routers.common.models import *

collection_name = "files"


def create_file(session: Database, file_model: FileDBModel):
    session[collection_name].insert_one(file_model.model_dump())
