from pymongo.database import Database
from src.routers.common.models import *

collection_name = "files"


def create_file(session: Database, file_model: FileDBModel):
    if session[collection_name].find_one({"file_name": file_model.file_name}):
        session[collection_name].replace_one(
            {"file_name": file_model.file_name}, file_model.model_dump()
        )
    else:
        session[collection_name].insert_one(file_model.model_dump())
