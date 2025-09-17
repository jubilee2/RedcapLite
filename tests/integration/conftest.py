import os
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from redcaplite import RedcapClient


API_URL = os.environ.get("REDCAP_API_URL")
API_TOKEN = os.environ.get("REDCAP_API_TOKEN")


@pytest.fixture
def client():
    """Provide a RedcapClient instance for integration tests."""
    if API_URL is None or API_TOKEN is None:
        pytest.skip("Integration test credentials not configured.")
    return RedcapClient(API_URL, API_TOKEN)
