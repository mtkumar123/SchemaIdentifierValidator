import pytest
import pandas as pd
from src.routers.validation import service
import os
from tests.conftest import mongo_client, test_db
from src.routers.schema.crud import collection_name as schema_collection_name
from src.routers.validation.crud import (
    collection_name as validation_collection_name,
)
from src.routers.common.models import *

data_dir = f"{os.path.dirname(__file__)}/data"
sample_rows = 100


@pytest.fixture()
def mock_reference_schema():
    schema = {
        "columns": ["number", "value", "name", "date"],
        "dtypes": ["int", "float", "str", "datetime"],
        "schema_mapping": {
            "number": "int",
            "value": "float",
            "name": "str",
            "date": "datetime",
        },
    }
    mongo_client[test_db][schema_collection_name].insert_one(schema)
    yield schema
    mongo_client[test_db][schema_collection_name].drop()


@pytest.fixture
def mock_file_in_db():
    schema = {
        "columns": ["number", "value", "name", "date"],
        "dtypes": ["int", "float", "str", "datetime"],
        "schema_mapping": {
            "number": "int",
            "value": "float",
            "name": "str",
            "date": "datetime",
        },
    }
    file_schema_db_model = FileDBModel(
        file_name="measurement.csv",
        file_size=10,
        file_location=f"{data_dir}/measurement.csv",
        schema_mapping=schema["schema_mapping"],
        columns=schema["columns"],
        dtypes=schema["dtypes"],
    )
    mongo_client[test_db][validation_collection_name].insert_one(
        file_schema_db_model.model_dump()
    )
    yield file_schema_db_model
    mongo_client[test_db][validation_collection_name].drop()


@pytest.fixture
def mock_file_without_schema_in_db():
    file_schema_db_model = FileDBModel(
        file_name="measurement.csv",
        file_size=10,
        file_location=f"{data_dir}/measurement.csv",
    )
    mongo_client[test_db][validation_collection_name].insert_one(
        file_schema_db_model.model_dump()
    )
    yield file_schema_db_model
    mongo_client[test_db][validation_collection_name].drop()


@pytest.fixture
def mock_bad_file_in_db():
    schema = {
        "columns": ["number", "value", "name", "date"],
        "dtypes": ["int", "float", "str", "datetime"],
        "schema_mapping": {
            "number": "int",
            "value": "float",
            "name": "str",
            "date": "datetime",
        },
    }
    file_schema_db_model = FileDBModel(
        file_name="measurement_bad.csv",
        file_size=10,
        file_location=f"{data_dir}/measurement_bad.csv",
        schema_mapping=schema["schema_mapping"],
        columns=schema["columns"],
        dtypes=schema["dtypes"],
    )
    mongo_client[test_db][validation_collection_name].insert_one(
        file_schema_db_model.model_dump()
    )
    yield file_schema_db_model
    mongo_client[test_db][validation_collection_name].drop()


def test_infer_dtypes():
    file_name = "people-100.csv"
    file_path = f"{data_dir}/{file_name}"
    df = pd.read_csv(file_path, nrows=sample_rows)
    inferred_dtypes = service.get_inferred_dtypes(df)
    assert inferred_dtypes == [
        "int",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "datetime",
        "str",
    ]

    file_name = "measurement.csv"
    file_path = f"{data_dir}/{file_name}"
    df = pd.read_csv(file_path, nrows=sample_rows)
    inferred_dtypes = service.get_inferred_dtypes(df)
    assert inferred_dtypes == ["int", "float", "str", "datetime"]


def test_get_cols_included():
    file_name = "people-100.csv"
    file_path = f"{data_dir}/{file_name}"
    df = pd.read_csv(file_path, nrows=sample_rows)
    has_cols, inferred_columns = service.get_columns(df)
    assert inferred_columns == [
        "Index",
        "User Id",
        "First Name",
        "Last Name",
        "Sex",
        "Email",
        "Phone",
        "Date of birth",
        "Job Title",
    ]


def test_get_cols_not_included():
    file_name = "measurement.csv"
    file_path = f"{data_dir}/{file_name}"
    df = pd.read_csv(file_path, nrows=sample_rows)
    has_cols, inferred_columns = service.get_columns(df)
    assert has_cols == False
    assert inferred_columns == []


def test_infer_cols_default():
    file_name = "measurement.csv"
    file_path = f"{data_dir}/{file_name}"
    df = pd.read_csv(file_path, nrows=sample_rows)
    result = service.infer_columns(mongo_client[test_db], df, [])
    assert result == ["Column0", "Column1", "Column2", "Column3"]


def test_infer_cols_reference(mock_reference_schema):
    file_name = "measurement.csv"
    file_path = f"{data_dir}/{file_name}"
    df = pd.read_csv(file_path, nrows=sample_rows)
    result = service.infer_columns(
        mongo_client[test_db], df, ["int", "float", "str", "datetime"]
    )
    assert result == mock_reference_schema["columns"]


def test_file_validation_success(mock_file_in_db):
    result = service.validate_file(
        mongo_client[test_db],
        mock_file_in_db.file_name,
    )
    assert result.validation_successful == True


def test_file_without_schema_validation_success(
    mock_file_without_schema_in_db,
):
    result = service.validate_file(
        mongo_client[test_db],
        mock_file_without_schema_in_db.file_name,
    )
    assert result.validation_successful == True


def test_file_validation_failure(
    mock_bad_file_in_db,
):
    result = service.validate_file(
        mongo_client[test_db],
        mock_bad_file_in_db.file_name,
    )
    assert result.validation_successful == False
    assert result.error
