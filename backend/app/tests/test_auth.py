import sys
import os
from unittest.mock import MagicMock

sys.modules['chromadb'] = MagicMock()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_unauthorized_documents_list():
    response = client.get("/documents/list")
    assert response.status_code == 401

def test_profile_requires_auth():
    response = client.get("/profile")
    assert response.status_code == 401
