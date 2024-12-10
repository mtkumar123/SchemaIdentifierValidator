from src.routers.schema.models import *
from pymongo.database import Database
from src.routers.schema import crud


def get_schemas(
    session: Database,
) -> list[SchemaResponse]:
    result: list[SchemaDBModel] = []
    result = crud.get_schemas(session)
    return [SchemaResponse(**obj.model_dump()) for obj in result]


def get_schemas_by_dtypes(
    session: Database,
    dtypes: list[str],
) -> list[SchemaResponse]:
    result: list[SchemaDBModel] = []
    result = crud.get_schemas(
        session, filter={"dtypes": {"$all": dtypes, "$size": len(dtypes)}}
    )
    return [SchemaResponse(**obj.model_dump()) for obj in result]


def get_schema_by_id(
    session: Database,
    schema_id: str,
) -> SchemaResponse:
    result = crud.get_schema_by_id(session, schema_id)
    return SchemaResponse(**result.model_dump())


def post_schema(
    session: Database,
    schema: NewSchemaRequest,
) -> SchemaResponse:
    result = crud.post_schema(session, SchemaDBModel(**schema.model_dump()))
    return SchemaResponse(**result.model_dump())


def put_schema(
    session: Database,
    schema_id: str,
    schema: dict[str, str],
) -> SchemaResponse:
    result = crud.put_schema(session, schema_id, schema)
    return SchemaResponse(**result.model_dump())
