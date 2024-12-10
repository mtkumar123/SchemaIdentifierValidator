import pandas as pd
from datetime import datetime
from dateutil import parser
from pymongo.database import Database
from src.routers.validation import crud
from src.routers.validation.models import *
from src.routers.common.models import *
from src.routers.schema import service as schema_service
from pydantic import BaseModel, create_model


def get_file_schema_details(
    session: Database, file_name: str
) -> FileSchemaDetailResponse:
    # First check the db if this has some stuff attached
    db_model = crud.get_file_schema_details_db(session, file_name)
    if db_model.schema_mapping:
        return FileSchemaDetailResponse(
            file_name=db_model.file_name,
            schema_mapping=db_model.schema_mapping,
            columns=db_model.columns,
            dtypes=db_model.dtypes,
        )
    else:
        # Now we have to do the inferring of the schema
        file_location = db_model.file_location
        inferred_schema = get_inferred_schema(session, file_location)
        columns = list(inferred_schema.keys())
        dtypes = list(inferred_schema.values())
        # Save the inferred schema so it can be reused
        crud.update_file_schema_details_db(
            session,
            file_name,
            FileDBModel(
                file_size=db_model.file_size,
                file_name=db_model.file_name,
                file_location=db_model.file_location,
                schema_mapping=inferred_schema,
                columns=columns,
                dtypes=dtypes,
            ),
        )
        return FileSchemaDetailResponse(
            file_name=db_model.file_name,
            schema_mapping=inferred_schema,
            columns=columns,
            dtypes=dtypes,
        )


def update_file_schema_details(
    session: Database,
    file_name: str,
    file_schema: UpdateFileSchemaRequest,
) -> FileSchemaDetailResponse:
    updated_file_schema_db_model: Optional[FileDBModel] = None
    # First get the file from db
    file_db_model = crud.get_file_schema_details_db(session, file_name)
    if file_schema.schema_id:
        # Get the schema from service
        schema = schema_service.get_schema_by_id(
            session, file_schema.schema_id
        )
        updated_file_schema_db_model = FileDBModel(
            file_name=file_db_model.file_name,
            file_location=file_db_model.file_location,
            file_size=file_db_model.file_size,
            columns=schema.columns,
            schema_mapping=schema.schema_mapping,
            dtypes=schema.dtypes,
        )
    else:
        updated_file_schema_db_model = FileDBModel(
            file_name=file_db_model.file_name,
            file_location=file_db_model.file_location,
            file_size=file_db_model.file_size,
            columns=list(file_schema.schema_mapping.keys()),
            schema_mapping=file_schema.schema_mapping,
            dtypes=list(file_schema.schema_mapping.values()),
        )
    crud.update_file_schema_details_db(
        session,
        file_name,
        updated_file_schema_db_model,
    )
    return FileSchemaDetailResponse(
        file_name=updated_file_schema_db_model.file_name,
        schema_mapping=updated_file_schema_db_model.schema_mapping,
        columns=updated_file_schema_db_model.columns,
        dtypes=updated_file_schema_db_model.dtypes,
    )


def _build_dynamic_pydantic_model(schema: dict[str, str]) -> BaseModel:
    fields = {}
    for col, type in schema.items():
        if type == "int":
            fields[col] = (int, ...)
        elif type == "float":
            fields[col] = (float, ...)
        elif type == "datetime":
            fields[col] = (datetime, ...)
        elif type == "str":
            fields[col] = (str, ...)
        else:
            fields[col] = (str, ...)
    return create_model("schema_validator", **fields)


def _file_validation(
    file_location: str, schema: dict[str, str]
) -> tuple[bool, Optional[str]]:
    df = pd.read_csv(file_location, names=list(schema.keys()))
    validator_model = _build_dynamic_pydantic_model(schema)
    for index, row in df.iterrows():
        try:
            validator_model(**row.to_dict())
        except Exception as exc:
            return False, f"Validation failed for row {index}: {row.to_dict()}"
    return True, None


def validate_file(
    session: Database, file_name: str
) -> FileValidateDetailResponse:
    # First get the file from db
    file_db_model = crud.get_file_schema_details_db(session, file_name)
    # Check that there is a schema populated
    if not file_db_model.schema_mapping:
        file_with_schema = get_file_schema_details(session, file_name)
        file_db_model.schema_mapping = file_with_schema.schema_mapping
        file_db_model.columns = file_with_schema.columns
        file_db_model.dtypes = file_with_schema.dtypes
    schema = file_db_model.schema_mapping
    result, error = _file_validation(file_db_model.file_location, schema)
    return FileValidateDetailResponse(
        file_name=file_db_model.file_name,
        schema_mapping=schema,
        columns=file_db_model.columns,
        dtypes=file_db_model.dtypes,
        validation_successful=result,
        error=error if error else None,
    )


def get_inferred_dtypes(df: pd.DataFrame) -> list[type]:
    result: list[str] = []
    for col in df.columns:
        series = df[col]
        if series.dtype.name == "int64":
            result.append("int")
        elif series.dtype.name == "float64":
            result.append("float")
        elif series.dtype.name == "object":
            try:
                parsed_col = pd.to_datetime(series)
                result.append("datetime")
                continue
            except:
                pass
            try:
                parsed_col = pd.to_numeric(series)
                if parsed_col.dtype.name == "int64":
                    result.append("int")
                elif parsed_col.dtype.name == "float64":
                    result.append("float")
                continue
            except:
                pass
            result.append("str")
    return result


def get_columns(df: pd.DataFrame) -> tuple[bool, list[str]]:
    result: list[str] = []
    has_cols = True
    for col in df.columns:
        try:
            int(col)
            has_cols = False
            break
        except:
            pass
        try:
            float(col)
            has_cols = False
            break
        except:
            pass
        try:
            parser.parse(col)
            has_cols = False
            break
        except:
            pass
        result.append(col)

    return has_cols, result


def infer_columns(
    session: Database, df: pd.DataFrame, dtypes: list[str]
) -> list[str]:
    # Check other schemas if they have the same dtypes
    schemas = schema_service.get_schemas_by_dtypes(session, dtypes)
    if schemas:
        return schemas[0].columns
    else:
        cols = []
        for i in range(df.shape[1]):
            cols.append(f"Column{i}")
        return cols


def get_inferred_schema(
    session: Database,
    file: str,
    sample_rows: int = 100,
) -> dict[str, str]:
    result = {}
    df = pd.read_csv(file, nrows=sample_rows)
    has_cols, columns = get_columns(df)
    if not has_cols:
        # Add back the first row
        temp_df = pd.DataFrame([df.columns])
        df.columns = temp_df.columns
        df = pd.concat([temp_df, df], ignore_index=True)
        dtypes = get_inferred_dtypes(df)
        columns = infer_columns(session, df, dtypes)
    else:
        dtypes = get_inferred_dtypes(df)
    for col, dtype in zip(columns, dtypes):
        result[col] = dtype
    return result
