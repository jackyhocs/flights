from pathlib import Path

import pytest

# not the most elegant way to file the root of the file to get the json contents
BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent


@pytest.fixture
def real_dataset_path() -> Path:
    return REPO_ROOT / "flights.json"
