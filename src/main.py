from fastapi import FastAPI
from src.routers.schema.router import router as schema_router
from src.routers.upload.router import router as upload_router
from src.routers.validation.router import router as validation_router
from src.utils import lifespan

app = FastAPI(
    lifespan=lifespan,
    title="Schema Inference and Validation",
    description="Inference and validation of schemas against csv files.",
    version="1.0.0",
)

app.include_router(schema_router)
app.include_router(upload_router)
app.include_router(validation_router)
