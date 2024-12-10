from fastapi import APIRouter, HTTPException, Header
from src.utils import MongoClientDep
from src.routers.upload import service
from fastapi import File, UploadFile, HTTPException
from starlette import status
from src.exceptions import FileTooLargeException, InvalidFileException
from src.routers.upload.models import *

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/", status_code=201)
def upload_file(
    session: MongoClientDep,
    file: UploadFile = File(
        ..., description="CSV File to be uploaded. Max file size is 100MB."
    ),
    content_length: int = Header(...),
) -> UploadedFileResponse:
    """
    Upload a file.
    """
    try:
        service.validate_file(file, content_length)
        response = service.upload_file(
            session,
            file,
        )
    except InvalidFileException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        )
    except FileTooLargeException as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=exc.message,
        )
    return response
