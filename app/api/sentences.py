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


@router.post("")
@version(1, 0)
def get_entity_sentences(entity_search: schemas.EntitySearch, skip: int = 0,
                         limit: int = 100, db: Session = Depends(get_db)):
    """
    Search for sentences by entity object by name.

    - :param entity_name: ID of selected entity
    - :param skip: number of sentence objects to skip
    - :param limit: max number of sentence objects to return
    - :return: list of sentences
    """
    db_entity = crud.get_entity_by_name(db, entity_name=entity_search.entity_name.strip())
    if not db_entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_search.entity_name} does not exist")
    db_entity_sents = crud.get_entity_sentences(db, db_entity=db_entity, skip=skip, limit=limit)
    print(db_entity_sents)
    return db_entity_sents
