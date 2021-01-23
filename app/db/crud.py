from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

from . import schemas, models


def get_request(db: Session, req_id: int):
    """
    Get request object by id.
    :param db: Session object.
    :param req_id: Request ID.
    :return: Request model.
    """
    return db.query(models.Request).filter(models.Request.id == req_id).first()


def get_request_by_path(db: Session, path: str):
    """
    Get request object by path.
    :param db: Session object.
    :param path: path in request.
    :return: Request model.
    """
    return db.query(models.Request).filter(models.Request.path == path).first()


def get_requests(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all requests from database paginated by skip and limit.
    :param db: Session object.
    :param skip: number of objects to skip.
    :param limit: max objects to return.
    :return: List of Request models.
    """
    return db.query(models.Request).offset(skip).limit(limit).all()


def create_request(db: Session, request: schemas.RequestCreate):
    """
    Add request to database. Sets request status to "Queued".
    :param db: Session object.
    :param request: Request object to create.
    :return: Created request model.
    """
    status = models.Statuses.Queued.name
    db_request = models.Request(path=request.path, status=status)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def update_request_status(db: Session, status: models.Statuses, db_request: models.Request):
    """
    Update status of request.
    :param db: Session object.
    :param status: New status.
    :param db_request: Request object to update.
    :return: Updated request object.
    """
    setattr(db_request, 'status', status.name)
    db.flush()
    db.commit()
    db.refresh(db_request)
    return db_request


def create_sentences(db: Session, req_id: int, sentences: List[schemas.SentenceCreate]):
    """
    Bulk add sentences of request with req_id to database.
    :param db: Session object.
    :param req_id: ID of request.
    :param sentences: List of sentences to add.
    :return: Number of sentences tagged to request.
    """
    for sent in sentences:
        db_sent = models.Sentence(req_id=req_id, text=sent.text)
        db.add(db_sent)
    db.commit()
    return db.query(models.Sentence).filter(models.Request.id == req_id).count()


def create_sentence(db: Session, req_id: int, sentence: str):
    """
    Add sentence of request with req_id to database.
    :param db: Session object.
    :param req_id: ID of request.
    :param sentence: Sentence object to add.
    :return: Created sentence model.
    """
    db_sent = models.Sentence(req_id=req_id, text=sentence)
    db.add(db_sent)
    db.commit()
    db.refresh(db_sent)
    return db_sent


def get_request_sentences(db: Session, req_id: int, skip: int = 0, limit: int = 100):
    """
    Get sentences of request with req_id paginated by skip and limit.
    :param db: Session object.
    :param req_id: ID of request.
    :param skip: number of objects to skip.
    :param limit: max objects to return.
    :return: List of Sentence models.
    """
    return db.query(models.Sentence).filter(models.Sentence.req_id == req_id).offset(skip).limit(limit).all()


def get_sentence(db: Session, sent_id: int):
    """
    Get sentence by id.
    :param db: Session object.
    :param sent_id: ID of sentence.
    :return: Sentence model.
    """
    return db.query(models.Sentence).filter(models.Sentence.id == sent_id).first()


def create_entities(db: Session, db_sent: models.Sentence, entities: List[schemas.EntityCreate]):
    """
    Bulk add entities of sentence to database.
    If entity already exist, adds association to sentence.
    If entity and association already exist, do nothing.

    :param db: Session object.
    :param db_sent: Sentence object that entities belong to.
    :param entities: List of entities to be created.
    :return: Count of created entities.
    """
    ctr = 0
    for entity in entities:

        db_entity = db.query(models.Entity).filter(models.Entity.name == entity.name).first()
        if db_entity:
            if db_sent in db_entity.sentences:
                continue
        else:
            db_entity = models.Entity(**entity.dict())

        db_entity.sentences.append(db_sent)
        db.add(db_entity)

        ctr += 1
    db.commit()
    return ctr


def get_entities(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all entities in database paginated by skip and limit.
    :param db: Session object.
    :param skip: number of objects to skip.
    :param limit: max objects to return.
    :return: List of entity models.
    """
    return db.query(models.Entity).offset(skip).limit(limit).all()


def get_entity(db: Session, entity_id: int):
    """
    Get entity by id.
    :param db: Session object.
    :param entity_id: ID of entity.
    :return: Entity object.
    """
    return db.query(models.Entity).filter(models.Entity.id == entity_id).first()


def get_entity_by_name(db: Session, entity_name: str):
    """
    Get entity by name.
    :param db: Session object.
    :param entity_name: Name of entity to look for.
    :return: Entity object.
    """
    # db.query(models.Entity).filter(models.Entity.name.ilike(f'%{entity_name}%')).first()
    return db.query(models.Entity).filter(func.lower(models.Entity.name) == func.lower(entity_name)).first()


def get_entity_sentences(db: Session, db_entity: models.Entity, skip: int = 0, limit: int = 100):
    """
    Get sentences associated with entity object paginated by skip and limit.
    :param db: Session object.
    :param db_entity: Entity object.
    :param skip: number of objects to skip.
    :param limit: max objects to return.
    :return: List of sentences associated to entity.
    """
    return db.query(models.Sentence.text).filter((models.Sentence.id == models.association_table.c.sent_id) &
                                                 (models.association_table.c.ent_id == db_entity.id)).offset(
        skip).limit(limit).all()


def update_requests_status(db: Session, original_statuses: List[models.Statuses], new_status: models.Statuses):
    """
    Bulk update all requests in database from original statuses to new status.
    :param db: Session object.
    :param original_statuses: List of old statuses to replace.
    :param new_status: New status to update to.
    :return: Number of updated requests.
    """
    old_statuses = [status.name for status in original_statuses]
    db_requests = db.query(models.Request).filter(models.Request.status.in_(old_statuses)).all()
    for db_request in db_requests:
        setattr(db_request, 'status', new_status.name)
    db.flush()
    db.commit()
    return len(db_requests)
