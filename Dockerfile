FROM python:3.12-slim

WORKDIR /code

COPY ./ ./

EXPOSE 8000

RUN pip install --no-cache-dir --upgrade -r ./src/requirements.txt

ENTRYPOINT ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
