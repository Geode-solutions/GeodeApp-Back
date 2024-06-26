def test_allowed_files(client):
    route = f"/opengeodeweb_back/allowed_files"
    response = client.post(route, json={"supported_feature": None})
    assert response.status_code == 200


def test_root(client):
    route = f"/"
    response = client.post(route)
    assert response.status_code == 200
    ID = response.json["ID"]
    assert type(ID) is str
