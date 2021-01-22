from . import crud
from .database import SessionLocal
from .schemas import EntityCreate

import spacy

nlp = spacy.load('en_core_web_sm')


def extract_and_store_entities(req_id: int, text: str) -> None:
    db = SessionLocal()

    ignore_entities = [
        'DATE',
        'CARDINAL',
        'ORDINAL',
        'TIME',
        'QUANTITY',
        'MONEY',
    ]

    try:
        docs = nlp(text)
        sentences = list(docs.sents)

        for sent in sentences:
            sent_entities = {}
            for ent in sent.ents:
                if ent.label_ not in ignore_entities:
                    ent_text = ent.text.strip()
                    if ent_text not in sent_entities:
                        sent_entities[ent_text] = EntityCreate(name=ent_text, ent_type=ent.label_)

            if sent_entities:
                db_sent = crud.create_sentence(db, req_id=req_id, sentence=sent.text)
                count = crud.create_entities(db, db_sent=db_sent, entities=list(sent_entities.values()))

    finally:
        db.close()
