from tests.conftest import client, mongo_client, test_db
import os
from src.routers.upload.crud import collection_name

data_dir = f"{os.path.dirname(__file__)}/data"


def test_upload_file_success():
    file_name = "county_uk.csv"
    file_path = f"{data_dir}/{file_name}"
    with open(file_path, "rb") as file:
        response = client.post(
            "/upload", files={"file": (file_name, file, "text/csv")}
        )
    assert response.status_code == 201
    assert response.json() == {"file_name": "county_uk.csv", "file_size": 2018}

    result = mongo_client[test_db][collection_name].find_one()
    assert result["file_name"] == "county_uk.csv"


def test_upload_file_failure_extension():
    file_name = "county_uk.txt"
    file_path = f"{data_dir}/{file_name}"
    with open(file_path, "rb") as file:
        response = client.post(
            "/upload", files={"file": (file_name, file, "text/csv")}
        )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file."}


def test_upload_file_failure_content_type():
    file_name = "county_uk.csv"
    file_path = f"{data_dir}/{file_name}"
    with open(file_path, "rb") as file:
        response = client.post(
            "/upload", files={"file": (file_name, file, "text/plain")}
        )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file."}


def test_upload_file_failure_size():
    file_name = "country_full.csv"
    file_path = f"{data_dir}/{file_name}"
    with open(file_path, "rb") as file:
        response = client.post(
            "/upload", files={"file": (file_name, file, "text/csv")}
        )
    assert response.status_code == 413
    assert response.json() == {"detail": "File size is too large."}


def test_upload_file_failure_content_length():
    file_name = "country_full.csv"
    file_path = f"{data_dir}/{file_name}"
    with open(file_path, "rb") as file:
        response = client.post(
            "/upload",
            files={"file": (file_name, file, "text/csv")},
            headers={"content-length": "2000"},
        )
    assert response.status_code == 413
    assert response.json() == {"detail": "File size is too large."}
