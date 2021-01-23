import string
import random
import logging
import time
from os import path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_versioning import VersionedFastAPI
from starlette.responses import RedirectResponse

from db.database import SessionLocal, engine
from db import schemas, crud, models
from api import ping, requests, sentences, entities

# setup loggers
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)  # the __name__ resolve to "main" since we are at the root of the project.

# create database engine
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title='NER Service')

# CORS
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Dependency Injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.include_router(ping.router)
app.include_router(requests.router, prefix="/requests", tags=["requests"])
app.include_router(entities.router, prefix="/entities", tags=["entities"])
app.include_router(sentences.router, prefix='/sentences', tags=['sentences'])

app = VersionedFastAPI(app)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware handler to add request logging and process timer.
    """
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.on_event("startup")
async def startup_event():
    """
    Startup event to "abruptly stopped" Requests to Error status.
    """
    db = SessionLocal()
    try:
        err_count = crud.update_requests_status(db, [models.Statuses.Queued, models.Statuses.Processing],
                                                models.Statuses.Error)
        logger.info(f"Updated {err_count} requests to Error state.")
    finally:
        db.close()


@app.get("/")
def main():
    """
    Redirect API service entry to API docs.
    """
    return RedirectResponse(url="/v1_0/docs")


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")
