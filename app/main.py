from typing import List
import time
import uvicorn
import requests
from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from db.database import SessionLocal, engine
from db import schemas, crud, models

from services.scraper_service import get_web_text, check_valid_url

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Process Timer
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.post("/requests/", response_model=schemas.Request)
async def create_request(request: schemas.RequestCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_request = crud.get_request_by_path(db, path=request.path)
    if db_request:
        if db_request.status == models.Statuses.Success:
            raise HTTPException(status_code=400, detail="Request has already been processed.")
        elif db_request.status == models.Statuses.Processing:
            raise HTTPException(status_code=400, detail="Request is being processed.")
    else:
        db_request = crud.create_request(db=db, request=request)

    if db_request:
        if check_valid_url(db_request.path):
            # Scrape web text
            background_tasks.add_task(get_web_text, db_request.id)
        # Otherwise, handle differently

    return db_request


@app.get("/requests/", response_model=List[schemas.Request])
def read_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = crud.get_requests(db, skip=skip, limit=limit)
    return requests


@app.get("/requests/{req_id}", response_model=schemas.Request)
def read_request(req_id: int, db: Session = Depends(get_db)):
    db_req = crud.get_request(db, req_id=req_id)
    if db_req is None:
        raise HTTPException(status_code=404, detail="URL request not found")
    return db_req


@app.post("/requests/{req_id}/sentences")
def create_sentences(req_id: int, sentences: List[schemas.SentenceCreate], db: Session = Depends(get_db)):
    # db_doc = crud.get_document_by_url(db, url=document.url)
    # if db_doc:
    #     raise HTTPException(status_code=400, detail="URL has already been processed.")
    return crud.create_sentences(db=db, req_id=req_id, sentences=sentences)


@app.get("/requests/{req_id}/sentences", response_model=List[schemas.Sentence])
def read_request_sentences(req_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_req_sents = crud.get_request_sentences(db, req_id=req_id, skip=skip, limit=limit)
    return db_req_sents


@app.post("/entities")
def create_sentence_entity(sent_id: int, entities: List[schemas.EntityCreate], db: Session = Depends(get_db)):
    db_sent = crud.get_sentence(db, sent_id)
    if not db_sent:
        raise HTTPException(status_code=400, detail=f"Sentence of id {sent_id} does not exist")
    return crud.create_entities(db=db, db_sent=db_sent, entities=entities)


@app.get("/entities/", response_model=List[schemas.Entity])
def read_entities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    entities = crud.get_entities(db, skip=skip, limit=limit)
    return entities


@app.get("/entities/search/")#, response_model=List[schemas.Sentence])
def search_entity_sentences(entity_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_entity = crud.get_entity_by_name(db, entity_name=entity_name)
    if not db_entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_name} does not exist")
    db_entity_sents = crud.get_entity_sentences(db, db_entity=db_entity, skip=skip, limit=limit)
    return db_entity_sents


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


# 127.0.0.1:8000/items/4?q=hello
# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Optional[str] = None):
#     return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")
