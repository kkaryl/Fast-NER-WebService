import json

from app.db import crud

VER = 'v1_0'


def test_read_entities(test_app):
    response = test_app.get(f"{VER}/entities/")
    assert response.status_code == 200


def test_read_entity(test_app):
    response = test_app.get(f"{VER}/entities/1")
    assert response.status_code == 200


def test_read_entity_invalid_id(test_app):
    response = test_app.get(f"{VER}/entities/999999999999999999")
    assert response.status_code == 404


def test_search_entity_sentences(test_app):
    response = test_app.get(f"{VER}/entities/1/sentences")
    assert response.status_code == 200


def test_search_entity_sentences_invalid_id(test_app):
    response = test_app.get(f"{VER}/entities/999999999999999999/sentences")
    assert response.status_code == 404
