import traceback
import logging
import requests
from bs4 import BeautifulSoup

from . import crud, models
from .models import Statuses
from .database import SessionLocal
from .nlp_service import extract_and_store_entities


def scrape_text_body(url: str):
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all(text=True)

    document = ''
    blacklist = [
        '[document]',
        'noscript',
        'header',
        'html',
        'meta',
        'head',
        'input',
        'script',
        'style',
        'link',
        # 'a',
    ]

    linebreaks = [
        '\n',
    ]

    for t in text:
        if t.parent.name not in blacklist:
            nt = t.strip()
            if nt and nt not in linebreaks:
                document += '{} '.format(nt)

    return document


def get_web_text(req_id: int):
    db = SessionLocal()
    db_request = crud.get_request(db, req_id=req_id)
    try:
        if db_request.status not in [Statuses.Queued.name, Statuses.Error.name]:
            return

        db_request = crud.update_request_status(db, models.Statuses.Processing, db_request)

        document = scrape_text_body(db_request.path)

        if document:
            extract_and_store_entities(req_id=req_id, text=document)

        db_request = crud.update_request_status(db, models.Statuses.Success, db_request)

    except Exception as e:
        logging.error(traceback.format_exc())
        crud.update_request_status(db, models.Statuses.Error, db_request)
    finally:
        db.close()
    return

