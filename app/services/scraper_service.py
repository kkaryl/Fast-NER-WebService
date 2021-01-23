import traceback
import logging
import requests
from bs4 import BeautifulSoup

from db.models import Statuses
from db.database import SessionLocal
from db import crud, models
from services.nlp_service import extract_and_store_entities

BLACKLIST = [
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


def check_valid_url(path: str) -> bool:
    """
    Helper function to check if request path is a valid URL.

    :param path: String path to check if is valid URL.
    :return bool: Returns True if path is valid URL, else False.
    """
    try:
        requests.get(path)
        return True
    except requests.ConnectionError:
        return False
    except:
        return False


def get_web_text(req_id: int) -> None:
    """
    Function that processes URL requests of pending statuses.

    :param req_id: Integer ID of request
    """
    db = SessionLocal()
    db_request = crud.get_request(db, req_id=req_id)
    try:
        if db_request.status not in [Statuses.Queued.name, Statuses.Error.name]:
            return

        db_request = crud.update_request_status(db, models.Statuses.Processing, db_request)

        document = _scrape_web_text_body(db_request.path)

        if document:
            extract_and_store_entities(req_id=req_id, text=document)

        db_request = crud.update_request_status(db, models.Statuses.Success, db_request)

    except Exception as e:
        logging.error(traceback.format_exc())
        crud.update_request_status(db, models.Statuses.Error, db_request)
    finally:
        db.close()


def _scrape_web_text_body(url: str) -> str:
    """
    Uses BeautifulSoup4 to scrap text body of web pages of URL.

    :param url: web page link
    :return extracted document string
    """
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all(text=True)

    document = ''

    linebreaks = ['\n', ]

    for t in text:
        if t.parent.name not in BLACKLIST:
            nt = t.strip()
            if nt and nt not in linebreaks:
                document += '{} '.format(nt)

    return document
