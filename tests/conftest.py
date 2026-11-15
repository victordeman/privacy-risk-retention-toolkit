import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture()
def project(tmp_path):
    """A throwaway copy of the project (config, data, answer sheet) so tests never touch the real source data."""
    dst = tmp_path / "proj"
    for d in ("config", "data", "answer_sheet"):
        shutil.copytree(ROOT / d, dst / d)
    for p in (dst / "data" / "source").glob("*.csv"):
        p.chmod(0o644)
    (dst / "output").mkdir()
    return dst


def write(path, text):
    Path(path).write_text(text, encoding="utf-8")
    return path
