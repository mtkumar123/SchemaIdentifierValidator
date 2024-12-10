from pydantic import (
    BaseModel,
    Field,
    BeforeValidator,
    model_validator,
)
from typing import Annotated


class SchemaResponse(BaseModel):
    id: str = Field(..., description="Id of schema.")
    schema_mapping: dict[str, str] = Field(
        ...,
        description="Schema is represented by column to data type mapping.",
    )
    columns: list[str] = Field(..., description="Columns of schema.")
    dtypes: list[str] = Field(..., description="Data types of schema.")


class BaseSchemaRequest(BaseModel):
    schema_mapping: dict[str, str] = Field(
        ...,
        description="Schema is represented by column to data type mapping.",
    )
    columns: list[str] = Field(
        ...,
        description="Columns of schema. Optional field, if not provided columns are extracted from schema.",
    )
    dtypes: list[str] = Field(
        ...,
        description="Data types of schema. Optional field, if not provided data types are extracted from schema.",
    )

    @model_validator(mode="before")
    @classmethod
    def populate_columns_dtypes(cls, data: dict) -> dict:
        if "columns" not in data:
            schema_mapping: dict = data.get("schema_mapping", {})
            data["columns"] = list(schema_mapping.keys())
        if "dtypes" not in data:
            schema_mapping: dict = data.get("schema_mapping", {})
            data["dtypes"] = list(schema_mapping.values())
        return data


class ModifySchemaRequest(BaseSchemaRequest):
    id: str = Field(..., description="Id of schema.")


class NewSchemaRequest(BaseSchemaRequest): ...


class SchemaDBModel(BaseModel):
    id: Annotated[str | None, BeforeValidator(str)] = Field(
        default=None,
        alias="_id",
    )
    columns: list[str]
    schema_mapping: dict[str, str]
    dtypes: list[str]

    class Config:
        populate_by_name = True
