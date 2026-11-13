from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

DEFENSES_FILE = Path(__file__).resolve().parents[3] / "configs" / "defenses.yaml"


@lru_cache(maxsize=1)
def defense_config() -> dict[str, Any]:
    return yaml.safe_load(DEFENSES_FILE.read_text(encoding="utf-8"))
