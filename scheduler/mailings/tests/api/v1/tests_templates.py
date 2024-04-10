from rest_framework import status


def test_list_mailing_templates_list_401(client):
    response = client.get("/api/v1/templates/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_mailing_template_retrieve_401(client):
    response = client.get("/api/v1/templates/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
