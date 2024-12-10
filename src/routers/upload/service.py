from fastapi import UploadFile
from tempfile import NamedTemporaryFile
from typing import IO
from src.exceptions import FileTooLargeException, InvalidFileException
from src.routers.upload import crud
import shutil
from src.config import get_settings
from pymongo.database import Database
from src.routers.upload.models import *
from src.routers.common.models import *

settings = get_settings()

ALLOWED_CONTENT_TYPES = ["text/csv"]
ALLOWED_EXTENSIONS = ["csv"]


def validate_file(file: UploadFile, content_length: int) -> int:
    if content_length > settings.max_file_size:
        raise FileTooLargeException()
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise InvalidFileException()
    if file.filename.rsplit(".", 1)[-1].lower() not in ALLOWED_EXTENSIONS:
        raise InvalidFileException()


def upload_file(session: Database, file: UploadFile) -> UploadedFileResponse:
    real_file_size = 0
    temp: IO = NamedTemporaryFile(delete=False)
    for chunk in file.file:
        real_file_size += len(chunk)
        if real_file_size > settings.max_file_size:
            raise FileTooLargeException()
        temp.write(chunk)
    temp.close()
    destination_path = f"{settings.upload_file_location}/{file.filename}"
    shutil.move(temp.name, destination_path)
    crud.create_file(
        session,
        FileDBModel(
            file_name=file.filename,
            file_size=file.size,
            file_location=destination_path,
        ),
    )
    return UploadedFileResponse(file_name=file.filename, file_size=file.size)
