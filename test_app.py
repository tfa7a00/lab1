from app import app

def test_add():
    client = app.test_client()
    response = client.get('/add?a=2&b=3')
    assert response.status_code == 200
    assert response.get_json()['result'] == 5

def test_divide_by_zero():
    client = app.test_client()
    response = client.get('/divide?a=4&b=0')
    assert response.status_code == 400
