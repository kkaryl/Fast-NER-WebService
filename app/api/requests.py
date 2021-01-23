from typing import List
import logging
from fastapi import Depends, APIRouter, HTTPException, BackgroundTasks
from fastapi_versioning import version
from sqlalchemy.orm import Session

from db.database import SessionLocal, engine
from db import schemas, crud, models

from services.scraper_service import get_web_text, check_valid_url

# get root logger
logger = logging.getLogger(__name__)

router = APIRouter()


# Dependency Injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.Request, status_code=201, summary='Create a request')
@version(1, 0)
async def create_request(request: schemas.RequestCreate, background_tasks: BackgroundTasks,
                         db: Session = Depends(get_db)):
    """
    Create a request to perform Named Entity Recognition.
    - :param request: Request object containing path
    - :return: request object
    """
    request_type = None
    if check_valid_url(request.path):
        request_type = 'URL'
    # Check for other request e.g. files

    if not request_type:
        raise HTTPException(status_code=422, detail="Unrecognized request path.")

    db_request = crud.get_request_by_path(db, path=request.path)
    if db_request:
        if db_request.status == models.Statuses.Success:
            raise HTTPException(status_code=400, detail="Request has already been processed.")
        elif db_request.status == models.Statuses.Processing:
            raise HTTPException(status_code=400, detail="Request is being processed.")
    else:
        db_request = crud.create_request(db=db, request=request)

    if db_request:
        if request_type == 'URL':
            # Scrape web text
            background_tasks.add_task(get_web_text, db_request.id)
        # Otherwise, handle differently

    return db_request


@router.get("/", response_model=List[schemas.Request])
@version(1, 0)
def read_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Gets all requests in database paginated by skip and limit.

    - :param skip: number of request objects to skip
    - :param limit: max number of request objects to return
    - :return: list of requests
    """
    requests = crud.get_requests(db, skip=skip, limit=limit)
    return requests


@router.get("/{req_id}", response_model=schemas.Request)
@version(1, 0)
def read_request(req_id: int, db: Session = Depends(get_db)):
    """
    Get request object by id.

    - :param req_id: ID of request
    - :return: request object
    """
    db_req = crud.get_request(db, req_id=req_id)
    if db_req is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return db_req


@router.get("/{req_id}/sentences", response_model=List[schemas.Sentence])
@version(1, 0)
def read_request_sentences(req_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all sentences in request of request id paginated by skip and limit.

    - :param req_id: ID of request
    - :param skip: number of sentence objects to skip
    - :param limit: max number of sentence objects to return
    - :return: list of sentences
    """
    db_req = crud.get_request(db, req_id=req_id)
    if db_req is None:
        raise HTTPException(status_code=400, detail="Request does not exist.")
    db_req_sents = crud.get_request_sentences(db, req_id=req_id, skip=skip, limit=limit)
    return db_req_sents
