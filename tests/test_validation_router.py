from src.routers.common.models import FileDBModel
from src.routers.validation.crud import (
    collection_name as validation_collection_name,
)
from src.routers.schema.crud import collection_name as schema_collection_name
from src.main import app
import pytest
from tests.conftest import test_db, client, mongo_client
from src.routers.validation import service
import os

data_dir = f"{os.path.dirname(__file__)}/data"


@pytest.fixture()
def mock_file():
    file = {
        "file_name": "measurement.csv",
        "file_size": 100,
        "file_location": f"{data_dir}/measurement.csv",
    }
    mongo_client[test_db][validation_collection_name].insert_one(file)
    yield file
    mongo_client[test_db].drop_collection(validation_collection_name)


@pytest.fixture()
def reference_schema():
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
    result = mongo_client[test_db][schema_collection_name].insert_one(schema)
    schema["id"] = str(result.inserted_id)
    yield schema
    mongo_client[test_db].drop_collection(schema_collection_name)


@pytest.fixture()
def bad_reference_schema():
    schema = {
        "columns": ["number", "value", "name", "date", "time"],
        "dtypes": ["int", "float", "str", "datetime", "datetime"],
        "schema_mapping": {
            "number": "int",
            "value": "float",
            "name": "str",
            "date": "datetime",
            "time": "datetime",
        },
    }
    mongo_client[test_db][schema_collection_name].insert_one(schema)
    yield schema
    mongo_client[test_db].drop_collection(schema_collection_name)


@pytest.fixture
def mock_file_for_validation_in_db():
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
def mock_bad_file_for_validation_in_db():
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


def test_get_file_inferred_schema_details(bad_reference_schema, mock_file):
    response = client.get(f"/validations/{mock_file['file_name']}")
    assert response.status_code == 200
    assert response.json()["schema_mapping"] == {
        "Column0": "int",
        "Column1": "float",
        "Column2": "str",
        "Column3": "datetime",
    }


def test_get_file_inferred_from_relevant_schema_details(
    reference_schema,
    mock_file,
):
    response = client.get(f"/validations/{mock_file['file_name']}")
    assert response.status_code == 200
    assert response.json()["schema_mapping"] == {
        "number": "int",
        "value": "float",
        "name": "str",
        "date": "datetime",
    }


def test_post_file_schema_by_schema(mock_file):
    schema = {
        "schema_mapping": {
            "number": "int",
            "value": "float",
            "name": "str",
            "date": "datetime",
        }
    }
    response = client.post(
        f"/validations/{mock_file['file_name']}/schema", json=schema
    )
    assert response.status_code == 201
    assert response.json()["schema_mapping"] == schema["schema_mapping"]


def test_post_file_schema_by_id(reference_schema, mock_file):
    response = client.post(
        f"/validations/{mock_file['file_name']}/schema",
        json={"schema_id": reference_schema["id"]},
    )
    assert response.status_code == 201
    assert (
        response.json()["schema_mapping"] == reference_schema["schema_mapping"]
    )


def test_valid_successful(mock_file_for_validation_in_db):
    response = client.post(
        f"/validations/{mock_file_for_validation_in_db.file_name}/validate"
    )
    assert response.status_code == 200
    assert response.json()["validation_successful"] == True


def test_valid_failure(mock_bad_file_for_validation_in_db):
    response = client.post(
        f"/validations/{mock_bad_file_for_validation_in_db.file_name}/validate"
    )
    assert response.status_code == 200
    assert response.json()["validation_successful"] == False
    assert response.json()["error"]
