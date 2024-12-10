from pydantic import BaseModel, model_validator, Field
from typing import Optional


class FileSchemaDetailResponse(BaseModel):
    file_name: str = Field(
        ..., description="The file name for which the schema was retrieved."
    )
    schema_mapping: dict[str, str] = Field(
        ..., description="Schema of the file."
    )
    columns: list[str] = Field(..., description="Columns of the schema.")
    dtypes: list[str] = Field(..., description="Data types of the schema.")


class FileValidateDetailResponse(BaseModel):
    file_name: str = Field(
        ..., description="The file name for which validation was done."
    )
    schema_mapping: dict[str, str] = Field(
        ..., description="Schema that was used for validation."
    )
    columns: list[str] = Field(..., description="Columns of the schema.")
    dtypes: list[str] = Field(..., description="Data types of the schema.")
    validation_successful: bool = Field(
        ..., description="Validation success state."
    )
    error: Optional[str] = Field(
        default=None, description="Error message in case validation failed."
    )


class UpdateFileSchemaRequest(BaseModel):
    schema_id: Optional[str] = Field(
        default=None,
        description="Id of the schema that should be used for this file. Either schema_id or schema_mapping should be provided.",
    )
    schema_mapping: Optional[dict[str, str]] = Field(
        default=None,
        description="Schema mapping that should be used for this file. Either schema_id or schema_mapping should be provided.",
    )

    @model_validator(mode="before")
    @classmethod
    def check_schema_id_or_schema_mapping(cls, data: dict) -> dict:
        if "schema_mapping" not in data and "schema_id" not in data:
            raise ValueError(
                "Either schema_id or schema_mapping must be provided.",
                UpdateFileSchemaRequest,
            )
        return data
