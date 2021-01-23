import json

VER = 'v1_0'


def test_get_entity_sentences(test_app):
    test_request_payload = {'entity_name': 'SQL'}
    response = test_app.post(f"{VER}/sentences", data=json.dumps(test_request_payload), )
    assert response.status_code == 200


def test_get_entity_sentences_invalid(test_app):
    test_request_payload = {'entity_name': '1'}
    response = test_app.post(f"{VER}/sentences", data=json.dumps(test_request_payload), )
    assert response.status_code == 404
