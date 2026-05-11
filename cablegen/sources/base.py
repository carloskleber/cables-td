"""
Classe base para fontes de dados online, com suporte a cache.
"""

from __future__ import annotations

import hashlib
import json
import time
from abc import ABC, abstractmethod
from pathlib import Path

from cablegen.models import CableEntry, CableFamily

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
CACHE_MAX_AGE_SECONDS = 30 * 24 * 3600  # 30 dias


class DataSource(ABC):
  """Interface base para fontes de dados de cabos."""

  @property
  @abstractmethod
  def name(self) -> str:
    """Nome identificador da fonte."""
    ...

  @abstractmethod
  def available_families(self) -> list[str]:
    """Lista famílias disponíveis nesta fonte."""
    ...

  @abstractmethod
  def _fetch_raw(self, family: str) -> list[dict]:
    """Busca dados brutos da fonte. Retorna lista de dicts serializáveis."""
    ...

  @abstractmethod
  def _parse_entries(self, family: str, raw_data: list[dict]) -> list[CableEntry]:
    """Converte dados brutos em CableEntry."""
    ...

  def fetch(self, family: str, force: bool = False) -> list[CableEntry]:
    """Busca cabos de uma família, usando cache quando disponível."""
    cache_key = f"{self.name}_{family}"
    if not force:
      cached = self._read_cache(cache_key)
      if cached is not None:
        print(f"  Cache hit: {self.name}/{family}")
        return self._parse_entries(family, cached)

    print(f"  Fetching: {self.name}/{family}...")
    raw = self._fetch_raw(family)
    self._write_cache(cache_key, raw)
    return self._parse_entries(family, raw)

  def _cache_path(self, key: str) -> Path:
    safe_key = hashlib.md5(key.encode()).hexdigest()
    return CACHE_DIR / f"{safe_key}.json"

  def _read_cache(self, key: str) -> list[dict] | None:
    path = self._cache_path(key)
    if not path.exists():
      return None
    try:
      data = json.loads(path.read_text(encoding="utf-8"))
      ts = data.get("timestamp", 0)
      if time.time() - ts > CACHE_MAX_AGE_SECONDS:
        return None
      return data.get("entries", [])
    except (json.JSONDecodeError, KeyError):
      return None

  def _write_cache(self, key: str, entries: list[dict]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = self._cache_path(key)
    data = {"timestamp": time.time(), "source": self.name, "entries": entries}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
