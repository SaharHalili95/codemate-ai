def test_health_reports_demo_mode(client):
    body = client.get("/").json()

    assert body["status"] == "healthy (demo)"
    assert body["llm_provider"] == "demo"


def test_upload_splits_file_into_function_chunks(uploaded):
    assert uploaded["success"] is True
    assert uploaded["chunks_created"] == 2
    assert uploaded["language"] == "python"


def test_upload_of_empty_file_is_rejected(client):
    response = client.post("/upload", files={"file": ("empty.py", "")})

    assert response.status_code == 400


def test_upload_of_binary_file_is_rejected(client):
    response = client.post("/upload", files={"file": ("image.png", b"\xff\xd8\xff")})

    assert response.status_code == 400


def test_stats_count_uploaded_chunks(client, uploaded):
    stats = client.get("/stats").json()

    assert stats["total_chunks"] == 2
    assert stats["languages"] == {"python": 2}


def test_search_returns_matching_chunk(client, uploaded):
    exact_chunk = "def login(username, password):\n    return authenticate(username, password)\n"

    body = client.post("/search", json={"query": exact_chunk, "min_score": 0}).json()

    assert body["total"] >= 1
    assert body["results"][0]["chunk"]["file_name"] == "auth.py"


def test_chat_answers_with_sources(client, uploaded):
    exact_chunk = "def login(username, password):\n    return authenticate(username, password)\n"

    body = client.post("/chat", json={"message": exact_chunk}).json()

    assert body["model_used"] == "demo"
    assert "auth.py" in body["message"]
    assert body["conversation_id"] == "new"


def test_chat_stream_streams_text(client, uploaded):
    response = client.post("/chat/stream", json={"message": "How does login work?"})

    assert response.status_code == 200
    assert "Demo mode" in response.text


def test_delete_file_removes_its_chunks(client, uploaded):
    deleted = client.delete("/files/auth.py").json()

    assert deleted["chunks_deleted"] == 2
    assert client.get("/stats").json()["total_chunks"] == 0
