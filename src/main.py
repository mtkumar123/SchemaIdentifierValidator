from fastapi import FastAPI
from src.routers.schema.router import router as schema_router
from src.routers.upload.router import router as upload_router
from src.routers.validation.router import router as validation_router
from src.utils import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(schema_router)
app.include_router(upload_router)
app.include_router(validation_router)
