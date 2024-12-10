from pydantic import BaseModel
from typing import Optional


class FileDBModel(BaseModel):
    file_name: str
    file_size: int
    file_location: str
    schema_mapping: Optional[dict[str, str]] = None
    columns: Optional[list[str]] = None
    dtypes: Optional[list[str]] = None
