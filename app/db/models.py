from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base


class Statuses(Enum):
    Queued = 1
    Processing = 2
    Success = 3
    Error = 4


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True)
    status = Column(String, index=True)

    sentences = relationship("Sentence", back_populates="request")


association_table = Table('association', Base.metadata,
                          Column('sent_id', Integer, ForeignKey('sentences.id')),
                          Column('ent_id', Integer, ForeignKey('entities.id'))
                          )


class Sentence(Base):
    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    req_id = Column(Integer, ForeignKey("requests.id"))

    request = relationship("Request", back_populates="sentences")
    entities = relationship("Entity",
                            secondary=association_table,
                            back_populates="sentences")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    ent_type = Column(String, index=True)
    # sent_id = Column(Integer, ForeignKey("sentences.id"))

    sentences = relationship("Sentence",
                             secondary=association_table,
                             back_populates="entities")
