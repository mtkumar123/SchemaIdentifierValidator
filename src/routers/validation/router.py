from fastapi import APIRouter, HTTPException
from src.routers.validation import service
from src.routers.validation.models import *
from src.exceptions import *
from starlette import status
from src.utils import MongoClientDep

router = APIRouter(prefix="/validations", tags=["validations"])


@router.get("/{file_name}")
def get_file_schema_details(
    session: MongoClientDep, file_name: str
) -> FileSchemaDetailResponse:
    """
    Get the schema details for a file. If the schema for a file
    was not provided the returned schema and columns have been inferred
    by the system.
    """
    try:
        result = service.get_file_schema_details(session, file_name)
    except FileNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found."
        )
    return result


@router.post("/{file_name}/schema", status_code=201)
def post_file_schema_details(
    session: MongoClientDep,
    file_name: str,
    file_schema: UpdateFileSchemaRequest,
):
    """
    Map a schema to a file either by reusing an existing schema that was added previously
    or by using a custom schema mapping.
    """
    try:
        result = service.update_file_schema_details(
            session,
            file_name,
            file_schema,
        )
    except FileNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found."
        )
    except SchemaNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schema not found."
        )
    return result


@router.post("/{file_name}/validate")
def validate_file(
    session: MongoClientDep,
    file_name: str,
) -> FileValidateDetailResponse:
    """
    Validate a file with the associated schema. In case a file did not
    have an associated schema attached, the inferred schema and columns
    will be used.
    """
    try:
        return service.validate_file(session, file_name)
    except FileNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found."
        )
