from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class FileCache:
    def __init__(self, base_dir: str = "data") -> None:
        self.base_path = Path(base_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe_key = key.replace("/", "_").replace(":", "_")
        return self.base_path / f"{safe_key}.json"

    def get(self, key: str, ttl_seconds: int) -> Any | None:
        path = self._path(key)
        if not path.exists():
            return None

        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            return None

        age = time.time() - payload.get("timestamp", 0)
        if age > ttl_seconds:
            return None
        return payload.get("data")

    def set(self, key: str, data: Any) -> None:
        path = self._path(key)
        payload = {"timestamp": time.time(), "data": data}
        path.write_text(json.dumps(payload, ensure_ascii=False, default=str, indent=2))
