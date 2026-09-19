import os
import sys

# Ajoute explicitement backend/ (le parent de tests/) à sys.path, pour que
# "from app.xxx import yyy" fonctionne partout (Windows local, CI Linux),
# indépendamment du comportement de pythonpath dans pytest.ini.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)