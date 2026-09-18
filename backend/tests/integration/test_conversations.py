"""
Nécessite PostgreSQL démarré (docker compose up -d) — ces tests écrivent
réellement en base via l'API, contrairement aux tests unitaires.
"""


def test_create_and_get_conversation(client):
    create_response = client.post("/api/conversations")
    assert create_response.status_code == 200
    conversation_id = create_response.json()["id"]

    get_response = client.get(f"/api/conversations/{conversation_id}")
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["id"] == conversation_id
    assert body["messages"] == []


def test_get_nonexistent_conversation_returns_404(client):
    response = client.get("/api/conversations/999999999")
    assert response.status_code == 404


def test_list_conversations_includes_created_one(client):
    create_response = client.post("/api/conversations")
    conversation_id = create_response.json()["id"]

    list_response = client.get("/api/conversations")
    assert list_response.status_code == 200
    ids = [c["id"] for c in list_response.json()]
    assert conversation_id in ids
