from src.routers.schema.crud import collection_name
from src.main import app
import pytest
import bson
from tests.conftest import test_db, client, mongo_client
from src.routers.schema import service


@pytest.fixture(autouse=True)
def mock_schemas():
    test_schemas = [
        {
            "columns": ["name", "salary", "country_code"],
            "dtypes": ["str", "float", "str"],
            "schema_mapping": {
                "name": "str",
                "salary": "float",
                "country_code": "str",
            },
        },
        {
            "columns": ["car", "model", "license_plate"],
            "dtypes": ["str", "str", "str"],
            "schema_mapping": {
                "car": "str",
                "model": "str",
                "license_plate": "str",
            },
        },
    ]
    mongo_client[test_db][collection_name].insert_many(test_schemas)
    for test_schema in test_schemas:
        test_schema["id"] = str(test_schema["_id"])
        del test_schema["_id"]
    yield test_schemas
    mongo_client[test_db][collection_name].drop()


def test_get_all_schemas(mock_schemas):
    response = client.get("/schemas")
    assert response.status_code == 200
    response = response.json()
    assert len(response) == 2
    assert response == mock_schemas


def test_get_schema_by_id(mock_schemas):
    response = client.get(f"/schemas/{mock_schemas[0]["id"]}")
    assert response.status_code == 200
    response = response.json()
    assert response == mock_schemas[0]


def test_get_schema_by_nonexistent_id(mock_schemas):
    fake_id = str(bson.ObjectId())
    response = client.get(f"/schemas/{fake_id}")
    assert response.status_code == 404


def test_post_schema():
    new_schema = {
        "schema_mapping": {
            "name": "str",
            "salary": "str",
            "country_code": "int",
        },
    }
    response = client.post("/schemas", json=new_schema)
    response.status_code == 201
    data = response.json()
    assert data["columns"] == ["name", "salary", "country_code"]
    assert data["dtypes"] == ["str", "str", "int"]

    result = mongo_client[test_db][collection_name].count_documents({})
    assert result == 3


def test_post_malformed_schema():
    new_schema = {
        "columns": ["game", "studio", "sold_count"],
    }
    response = client.post("/schemas", json=new_schema)
    response.status_code == 422


def test_put_schema(mock_schemas):
    updated_schema = mock_schemas[0]
    updated_schema["columns"] = ["game", "studio", "sold_count"]
    response = client.put(
        f"/schemas/{mock_schemas[0]["id"]}",
        json=updated_schema,
    )
    assert response.status_code == 200
    assert response.json() == updated_schema


def test_get_schema_by_dtypes(mock_schemas):
    dtypes = mock_schemas[0]["dtypes"]
    result = service.get_schemas_by_dtypes(
        mongo_client[test_db],
        dtypes,
    )
    assert len(result) == 1
    assert result[0].dtypes == dtypes
