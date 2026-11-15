"""Shared helpers: safe CSV I/O, masking, dates, hashing, paths."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

log = logging.getLogger("privacy_toolkit")


class DataFileError(Exception):
    """A data file could not be read safely."""


@dataclass
class CsvData:
    fieldnames: list
    rows: list
    warnings: list = field(default_factory=list)


def read_csv(path) -> CsvData:
    """Read a CSV defensively. Raises DataFileError for unreadable input."""
    path = Path(path)
    if not path.is_file():
        raise DataFileError(f"{path.name}: file not found")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise DataFileError(f"{path.name}: cannot be read ({exc.__class__.__name__})") from exc
    if not raw.strip():
        raise DataFileError(f"{path.name}: file is empty")
    if b"\x00" in raw[:8192]:
        raise DataFileError(f"{path.name}: binary content, not a CSV")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DataFileError(f"{path.name}: not valid UTF-8") from exc
    try:
        reader = csv.reader(io.StringIO(text))
        header = next(reader)
        header = [h.strip() for h in header]
        if not any(header) or len(set(header)) != len(header):
            raise DataFileError(f"{path.name}: header row is blank or has duplicate column names")
        rows, warnings = [], []
        for n, rec in enumerate(reader, start=2):
            if not rec:
                continue
            if len(rec) != len(header):
                warnings.append(f"line {n}: expected {len(header)} fields, found {len(rec)} - row skipped")
                continue
            rows.append(dict(zip(header, rec)))
    except csv.Error as exc:
        raise DataFileError(f"{path.name}: malformed CSV ({exc})") from exc
    return CsvData(header, rows, warnings)


def write_csv(path, fieldnames, rows) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def load_json(path) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataFileError(f"{Path(path).name}: cannot load configuration ({exc})") from exc


def write_json(path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------- hashing
def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_tree(folder, pattern="*.csv") -> dict:
    folder = Path(folder)
    return {p.name: sha256_file(p) for p in sorted(folder.glob(pattern))}


# ---------------------------------------------------------------- masking
def mask_value(category: str, value: str) -> str:
    """Return a masked form of a value. Raw personal data must never reach logs or reports."""
    v = (value or "").strip()
    if not v:
        return ""
    if category == "email" and "@" in v:
        local, _, domain = v.partition("@")
        return f"{local[:1]}***@{domain}"
    if category == "phone":
        digits = re.sub(r"\D", "", v)
        return "*" * max(len(digits) - 2, 0) + digits[-2:]
    if category == "name":
        return " ".join(w[:1] + "***" for w in v.split())
    if category == "identification_number":
        return v[:3] + "*" * max(len(v) - 3, 0)
    if category == "ip_address":
        return v.split(".")[0] + ".*.*.*"
    return v[:1] + "***"


# ---------------------------------------------------------------- dates
def parse_date(value) -> date | None:
    """Parse YYYY-MM-DD (optionally followed by a time). Returns None when not a real date."""
    v = (value or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})(?:[ T]\d{2}:\d{2}(?::\d{2})?)?$", v)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def add_years(d: date, years: int) -> date:
    """Add whole years. 29 Feb rolls to 28 Feb when the target year is not a leap year."""
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)


def today_iso() -> str:
    return datetime.now().date().isoformat()


# ---------------------------------------------------------------- paths
@dataclass
class Paths:
    root: Path

    def __post_init__(self):
        self.root = Path(self.root).resolve()

    @property
    def config(self): return self.root / "config"
    @property
    def source(self): return self.root / "data" / "source"
    @property
    def registers(self): return self.root / "data" / "registers"
    @property
    def answer(self): return self.root / "answer_sheet"
    @property
    def output(self): return self.root / "output"
