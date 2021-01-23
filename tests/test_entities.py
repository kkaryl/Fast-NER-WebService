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

# def test_create_request_invalid_json(test_app):
#     test_request_payload = {'path': 'abc'}
#     response = test_app.post(f"{VER}/requests/", data=json.dumps(test_request_payload), )
#     assert response.status_code == 422
#
#
# def test_read_requests(test_app):
#     response = test_app.get(f"{VER}/requests/")
#     assert response.status_code == 200
#
#
# def test_read_request(test_app):
#     response = test_app.get(f"{VER}/requests/1")
#     assert response.status_code == 200
#
#
# def test_read_request_incorrect_id(test_app):
#     response = test_app.get(f"{VER}/requests/9999999999")
#     assert response.status_code == 404
#
#
# def test_read_request_sentences(test_app):
#     response = test_app.get(f"{VER}/requests/1/sentences")
#     assert response.status_code == 200
#
#
# def test_read_request_sentences_invalid_id(test_app):
#     response = test_app.get(f"{VER}/requests/9999999999/sentences")
#     assert response.status_code == 400
