from typing import List
import logging
from fastapi import Depends, APIRouter, HTTPException
from fastapi_versioning import version
from sqlalchemy.orm import Session

from db.database import SessionLocal, engine
from db import schemas, crud, models

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


@router.get("", response_model=List[schemas.Entity])
@version(1, 0)
def read_entities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Gets all entities in database paginated by skip and limit.

    - :param skip: number of entity objects to skip
    - :param limit: max number of entity objects to return
    - :param db: injected database
    - :return: list of entities
    """
    entities = crud.get_entities(db, skip=skip, limit=limit)
    return entities


@router.get("/{entity_id}", response_model=schemas.Entity)
@version(1, 0)
def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """
    Get entity object by id.

    - :param entity_id: ID of selected entity
    - :param db: injected database
    - :return: list of sentences
    """
    db_entity = crud.get_entity(db, entity_id=entity_id)
    if not db_entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} does not exist")
    return db_entity


@router.get("/{entity_id}/sentences")
@version(1, 0)
def search_entity_sentences(entity_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Search for sentences by entity object by id.

    - :param entity_id: ID of selected entity
    - :param skip: number of sentence objects to skip
    - :param limit: max number of sentence objects to return
    - :return: list of sentences
    """
    db_entity = crud.get_entity(db, entity_id=entity_id)
    if not db_entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} does not exist")
    db_entity_sents = crud.get_entity_sentences(db, db_entity=db_entity, skip=skip, limit=limit)
    return db_entity_sents
