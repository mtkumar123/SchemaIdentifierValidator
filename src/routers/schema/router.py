from fastapi import APIRouter, HTTPException
from src.routers.schema.models import *
from src.utils import MongoClientDep
from src.routers.schema import service
from starlette import status
from src.exceptions import SchemaNotFoundException

router = APIRouter(prefix="/schemas", tags=["schemas"])


@router.get("/")
def get_schemas(
    session: MongoClientDep,
) -> list[SchemaResponse]:
    """
    Obtain all schemas that were added by user.
    """
    return service.get_schemas(session)


@router.get("/{schema_id}")
def get_schema_by_id(
    session: MongoClientDep,
    schema_id: str,
) -> SchemaResponse:
    """
    Obtain schema by id.
    """
    try:
        result = service.get_schema_by_id(session, schema_id)
    except SchemaNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
        )
    return result


@router.post("/", status_code=201)
def post_schema(
    session: MongoClientDep,
    schema: NewSchemaRequest,
) -> SchemaResponse:
    """
    Add new schema that can be reused.
    """
    return service.post_schema(session, schema)


@router.put("/{schema_id}")
def put_schema(
    session: MongoClientDep,
    schema_id: str,
    schema: ModifySchemaRequest,
) -> SchemaResponse:
    """
    Modify an existing schema.
    """
    return service.put_schema(session, schema_id, schema)
