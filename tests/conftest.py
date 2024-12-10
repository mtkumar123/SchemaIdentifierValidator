import pytest
from src.config import get_settings
from pymongo import MongoClient
from src.main import app
from fastapi.testclient import TestClient
from src.utils import get_database
import os
import shutil

settings = get_settings()
settings.upload_file_location = "./test_file_uploads"
settings.max_file_size = 2500
mongo_client = MongoClient(
    host=settings.mongo_db_url,
    port=settings.mongo_db_port,
)

test_db = "tests"


def mock_get_database():
    return mongo_client[test_db]


app.dependency_overrides[get_database] = mock_get_database
client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_database():
    yield
    mongo_client.drop_database(test_db)


@pytest.fixture(autouse=True, scope="module")
def setup_file_upload_dir():
    os.makedirs(settings.upload_file_location, exist_ok=True)
    yield
    shutil.rmtree(settings.upload_file_location)
