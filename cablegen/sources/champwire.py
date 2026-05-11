"""
Scraper para dados de cabos do site ChampWire.

Fonte: https://champwire.com/product-type/transmission-distribution-cable/
Dados de catálogo público de fabricante.
"""

from __future__ import annotations

import re
import time

from cablegen.models import CableEntry
from cablegen.sources.base import DataSource

_BASE_URL = "https://champwire.com"

INCH_TO_MM = 25.4
LB_PER_1000FT_TO_KG_PER_KM = 1.48816394357
LBF_TO_KN = 0.0044482216153
OHM_PER_1000FT_TO_OHM_PER_KM = 3.280839895

# URLs das páginas de produto por família
_FAMILY_URLS: dict[str, list[str]] = {
  "AAC": ["/aluminum-conductor/"],
  "AAAC": ["/aluminum-conductor/"],
  "ACAR": ["/aluminum-conductor/"],
  "ACSR": ["/aluminum-conductor/"],
  "ACSR_AW": ["/aluminum-conductor/"],
  "ACSR_TW": ["/aluminum-conductor/"],
  "ACSS": ["/aluminum-conductor/"],
  "ACSS_AW": ["/aluminum-conductor/"],
  "ACSS_TW": ["/aluminum-conductor/"],
  "COPPER": ["/copper-conductor/"],
}


class ChampWireSource(DataSource):
  """Scraper para tabelas HTML do ChampWire."""

  @property
  def name(self) -> str:
    return "champwire"

  def available_families(self) -> list[str]:
    return list(_FAMILY_URLS.keys())

  def _fetch_raw(self, family: str) -> list[dict]:
    """Faz scraping das tabelas HTML do ChampWire.

    Requer beautifulsoup4 e requests.
    """
    try:
      import requests
      from bs4 import BeautifulSoup
    except ImportError:
      print("  Aviso: Instale 'requests' e 'beautifulsoup4' para usar esta fonte.")
      print("    pip install requests beautifulsoup4")
      return []

    urls = _FAMILY_URLS.get(family.upper(), [])
    if not urls:
      return []

    results: list[dict] = []
    for path in urls:
      url = _BASE_URL + path
      try:
        resp = requests.get(url, timeout=30, headers={
          "User-Agent": "cables-td-generator/0.1 (educational/research)",
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

      time.sleep(1)  # Rate limiting

    return results

  def _parse_html_table(self, table: object, family: str) -> list[dict]:
    """Extrai dados de uma tabela HTML."""
    try:
      from bs4 import Tag
    except ImportError:
      return []

    if not isinstance(table, Tag):
      return []

    rows = table.find_all("tr")
    if len(rows) < 2:
      return []

    # Extrair cabeçalhos
    header_row = rows[0]
    headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
    if not headers:
      return []

    results: list[dict] = []
    for row in rows[1:]:
      cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
      if len(cells) != len(headers):
        continue
      row_dict = {"_family": family}
      for h, c in zip(headers, cells):
        row_dict[h] = c
      results.append(row_dict)

    return results

  def _parse_entries(self, family: str, raw_data: list[dict]) -> list[CableEntry]:
    """Converte dados brutos do ChampWire em CableEntry."""
    entries: list[CableEntry] = []

    for row in raw_data:
      def _get_float(keys: list[str]) -> float | None:
        for k in keys:
          v = row.get(k, "").strip()
          if v:
            v = re.sub(r"[^\d.\-eE+]", "", v)
            try:
              return float(v)
            except ValueError:
              continue
        return None

      code = row.get("Code Word", row.get("Code", row.get("Name", ""))).strip()
      if not code:
        continue

      diam_in = _get_float(["OD (in)", "Diameter (in)", "OD"])
      weight_lbs_1000ft = _get_float(["Weight (lbs/1000ft)", "Weight"])
      strength_lbf = _get_float(["Rated Strength (lbs)", "Breaking Strength"])
      dc_resist_ohm_1000ft = _get_float(["DC Resistance", "Resistance"])

      entries.append(CableEntry(
        code_word=code,
        size_awg_kcmil=row.get("Size AWG or kcmil", row.get("Size", None)),
        stranding=row.get("Stranding", None),
        conductor_diameter_mm=diam_in * INCH_TO_MM if diam_in is not None else None,
        mass_total_kg_km=(
          weight_lbs_1000ft * LB_PER_1000FT_TO_KG_PER_KM
          if weight_lbs_1000ft is not None else None
        ),
        rated_strength_kn=strength_lbf * LBF_TO_KN if strength_lbf is not None else None,
        dc_resist_20c_ohm_km=(
          dc_resist_ohm_1000ft * OHM_PER_1000FT_TO_OHM_PER_KM
          if dc_resist_ohm_1000ft is not None else None
        ),
        source=f"ChampWire ({family})",
      ))

    return entries


def get_source() -> ChampWireSource:
  """Retorna instância do scraper ChampWire."""
  return ChampWireSource()
