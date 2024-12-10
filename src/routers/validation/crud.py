from pymongo.database import Database
from src.exceptions import FileNotFoundException
from src.routers.common.models import *

collection_name = "files"


def get_file_schema_details_db(
    session: Database,
    file_name: str,
) -> FileDBModel:
    result = session[collection_name].find_one({"file_name": file_name})
    if not result:
        raise FileNotFoundException()
    file_schema_db_model = FileDBModel(**result)
    return file_schema_db_model


def update_file_schema_details_db(
    session: Database,
    file_name: str,
    file_with_schema: FileDBModel,
):
    session[collection_name].replace_one(
        {"file_name": file_name},
        file_with_schema.model_dump(),
    )
