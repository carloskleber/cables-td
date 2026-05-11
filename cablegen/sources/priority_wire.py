"""
Scraper para dados de cabos do site Priority Wire.

Fonte: https://www.prioritywire.com/
"""

from __future__ import annotations

import re
import time

from cablegen.models import CableEntry
from cablegen.sources.base import DataSource

_BASE_URL = "https://www.prioritywire.com"

# URLs das páginas de produto por família
_FAMILY_URLS: dict[str, list[str]] = {
  "AAC": ["/product-catalog.php?cat=Bare-Aluminum-Conductors-12"],
  "AAAC": ["/product-catalog.php?cat=Bare-Aluminum-Conductors-12"],
  "ACAR": ["/product-catalog.php?cat=Bare-Aluminum-Conductors-12"],
  "ACSR": ["/product-catalog.php?cat=Bare-Aluminum-Conductors-12"],
}


class PriorityWireSource(DataSource):
  """Scraper para tabelas HTML da Priority Wire."""

  @property
  def name(self) -> str:
    return "priority_wire"

  def available_families(self) -> list[str]:
    return list(_FAMILY_URLS.keys())

  def _fetch_raw(self, family: str) -> list[dict]:
    try:
      import requests
      from bs4 import BeautifulSoup
    except ImportError:
      print("  Aviso: Instale 'requests' e 'beautifulsoup4' para usar esta fonte.")
      return []

    import urllib3
    urllib3.disable_warnings()

    urls = _FAMILY_URLS.get(family.upper(), [])
    if not urls:
      return []

    results: list[dict] = []
    for path in urls:
      url = _BASE_URL + path
      try:
        resp = requests.get(url, timeout=30, verify=False, headers={
          "User-Agent": "Mozilla/5.0",
        })
        resp.raise_for_status()
      except requests.RequestException as exc:
        print(f"  Aviso: Erro ao acessar {url}: {exc}")
        continue

      soup = BeautifulSoup(resp.text, "html.parser")
      tables = soup.find_all("table")

      for table in tables:
        parsed = self._parse_html_table(table, family)
        results.extend(parsed)

      time.sleep(1)

    return results

  def _parse_html_table(self, table: object, family: str) -> list[dict]:
    try:
      from bs4 import Tag
    except ImportError:
      return []

    if not isinstance(table, Tag):
      return []

    rows = table.find_all("tr")
    if len(rows) < 2:
      return []

    header_row = rows[0]
    headers = [th.get_text(strip=True).replace('\n', ' ') for th in header_row.find_all(["th", "td"])]
    if not headers:
      return []

    results: list[dict] = []
    for row in rows[1:]:
      cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
      if not cells:
        continue
      
      row_dict = {"_family": family}
      for i, c in enumerate(cells):
        if i < len(headers):
          row_dict[headers[i]] = c
      results.append(row_dict)

    return results

  def _parse_entries(self, family: str, raw_data: list[dict]) -> list[CableEntry]:
    entries: list[CableEntry] = []
    seen: set[str] = set()

    for row in raw_data:
      def _get_float(keys: list[str]) -> float | None:
        for k in keys:
          for row_k, v in row.items():
            if k.lower() in row_k.lower() and v.strip():
              val = re.sub(r"[^\d.\-eE+]", "", v)
              try:
                return float(val)
              except ValueError:
                continue
        return None

      code = None
      for k, v in row.items():
        if "code" in k.lower() or "word" in k.lower() or "name" in k.lower():
          if v.strip() and v.strip().isalpha():
            code = v.strip().title()
            break
      
      if not code:
        continue

      key = code.upper()
      if key in seen:
        continue
      seen.add(key)

      # Conversões:
      # Diametro (inches) -> mm (* 25.4)
      # Peso (lbs/1000ft) -> kg/km (* 1.48816)
      # Rated Strength (lbs) -> kN (* 0.00444822)
      
      diam_in = _get_float(["OD", "Diameter", "O.D."])
      weight_lbs = _get_float(["Weight", "lbs"])
      strength_lbs = _get_float(["Strength", "Breaking"])

      diam_mm = diam_in * 25.4 if diam_in is not None else None
      weight_kg_km = weight_lbs * 1.48816 if weight_lbs is not None else None
      strength_kn = strength_lbs * 0.00444822 if strength_lbs is not None else None

      entries.append(CableEntry(
        code_word=code,
        conductor_diameter_mm=diam_mm,
        mass_total_kg_km=weight_kg_km,
        rated_strength_kn=strength_kn,
        source=f"Priority Wire ({family})",
      ))

    return entries

def get_source() -> PriorityWireSource:
  return PriorityWireSource()
