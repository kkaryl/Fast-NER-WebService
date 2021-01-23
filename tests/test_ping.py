
def test_ping(test_app):
    # pytest .
    response = test_app.get("/v1_0/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}