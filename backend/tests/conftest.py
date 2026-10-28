import os
import tempfile

os.environ["DEMO_MODE"] = "true"
os.environ["CHROMA_PATH"] = tempfile.mkdtemp()

import pytest
from fastapi.testclient import TestClient

from app.main import app

SAMPLE_CODE = """def login(username, password):
    return authenticate(username, password)

def logout(user_id):
    return end_session(user_id)
"""


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
        for file_name in ("auth.py", "empty.py"):
            test_client.delete(f"/files/{file_name}")


@pytest.fixture
def uploaded(client):
    response = client.post("/upload", files={"file": ("auth.py", SAMPLE_CODE)})
    assert response.status_code == 200
    return response.json()
