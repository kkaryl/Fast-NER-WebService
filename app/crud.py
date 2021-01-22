from typing import List
from sqlalchemy.orm import Session

from . import models, schemas


def get_request(db: Session, req_id: int):
    return db.query(models.Request).filter(models.Request.id == req_id).first()


def get_request_by_path(db: Session, path: str):
    return db.query(models.Request).filter(models.Request.path == path).first()


def get_requests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Request).offset(skip).limit(limit).all()


def create_request(db: Session, request: schemas.RequestCreate):
    status = models.Statuses.Queued.name
    db_request = models.Request(path=request.path, status=status)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def update_request_status(db: Session, status: models.Statuses, db_request: models.Request):
    setattr(db_request, 'status', status.name)
    db.flush()
    db.commit()
    db.refresh(db_request)
    return db_request


def create_sentences(db: Session, req_id: int, sentences: List[schemas.SentenceCreate]):
    for sent in sentences:
        db_sent = models.Sentence(req_id=req_id, text=sent.text)
        db.add(db_sent)
    db.commit()
    return db.query(models.Sentence).filter(models.Request.id == req_id).count()


def create_sentence(db: Session, req_id: int, sentence: str):
    db_sent = models.Sentence(req_id=req_id, text=sentence)
    db.add(db_sent)
    db.commit()
    db.refresh(db_sent)
    return db_sent

def get_request_sentences(db: Session, req_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Sentence).filter(models.Sentence.req_id == req_id).offset(skip).limit(limit).all()


def get_sentence(db: Session, sent_id: int):
    return db.query(models.Sentence).filter(models.Sentence.id == sent_id).first()


def create_entities(db: Session, db_sent: models.Sentence, entities: List[schemas.EntityCreate]):
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
    return db.query(models.Entity).offset(skip).limit(limit).all()


def get_entity_by_name(db: Session, entity_name: str):
    return db.query(models.Entity).filter(models.Entity.name == entity_name).first()


def get_entity_sentences(db: Session, db_entity: models.Entity, skip: int = 0, limit: int = 100):
    return db.query(models.Sentence.text).filter((models.Sentence.id == models.association_table.c.sent_id) &
                                                 (models.association_table.c.ent_id == db_entity.id)).offset(skip).limit(limit).all()


# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()
#
#
# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
