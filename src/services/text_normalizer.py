from __future__ import annotations

import re
import unicodedata


def normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ASCII", "ignore").decode("ASCII")
    lowered = ascii_text.lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", lowered)).strip()
