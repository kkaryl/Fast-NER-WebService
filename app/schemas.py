from typing import List, Optional

from pydantic import BaseModel
from pydantic.main import ForwardRef


class EntityBase(BaseModel):
    name: str
    ent_type: str


class EntityCreate(EntityBase):
    pass


# Sentences = ForwardRef("List[Sentence]")


class Entity(EntityBase):
    id: int
    # sent_id: int
    # sentences: Sentences = []

    class Config:
        orm_mode = True


class SentenceBase(BaseModel):
    text: str


class SentenceCreate(SentenceBase):
    pass


class Sentence(SentenceBase):
    id: int
    req_id: int
    entities: List[Entity] = []

    class Config:
        orm_mode = True

# Entity.update_forward_refs()

class RequestBase(BaseModel):
    path: str


class RequestCreate(RequestBase):
    pass


class Request(RequestBase):
    id: int
    status: str
    sentences: List[Sentence] = []

    class Config:
        orm_mode = True


class Association(BaseModel):
    sent_id: int
    ent_id: int

    class Config:
        orm_mode = True