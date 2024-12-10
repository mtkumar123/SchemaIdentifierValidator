from pymongo.database import Database
from bson import ObjectId
from src.routers.schema.models import *
from typing import Any, Optional
from src.exceptions import SchemaNotFoundException

collection_name = "schemas"


def post_schema(
    session: Database,
    db_model: SchemaDBModel,
) -> SchemaDBModel:
    result = session[collection_name].insert_one(
        db_model.model_dump(exclude_none=True)
    )
    post_result = session[collection_name].find_one(
        {"_id": result.inserted_id}
    )
    return SchemaDBModel(**post_result)


def put_schema(
    session: Database,
    id: str,
    db_model: SchemaDBModel,
) -> SchemaDBModel:
    if db_model.id == None:
        db_model.id = id
    session[collection_name].replace_one(
        {"_id": ObjectId(id)}, db_model.model_dump()
    )
    updated_result = session[collection_name].find_one({"_id": ObjectId(id)})
    return SchemaDBModel(**updated_result)


def get_schemas(
    session: Database,
    filter: Optional[dict[str, Any]] = None,
) -> list[SchemaDBModel]:
    if filter:
        return [
            SchemaDBModel(**schema)
            for schema in session[collection_name].find(filter)
        ]
    return [
        SchemaDBModel(**schema) for schema in session[collection_name].find()
    ]


def get_schema_by_id(
    session: Database,
    schema_id: str,
) -> Optional[SchemaDBModel]:
    result = session[collection_name].find_one({"_id": ObjectId(schema_id)})
    if not result:
        raise SchemaNotFoundException()
    schema_db_model = SchemaDBModel(**result)
    return schema_db_model
