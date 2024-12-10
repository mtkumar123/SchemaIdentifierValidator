from pydantic import BaseModel


class UploadedFileResponse(BaseModel):
    file_name: str
    file_size: int
