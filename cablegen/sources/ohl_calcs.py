"""
Importador de dados do repositório ohl-calcs (GitHub).

Fonte: https://github.com/LiaungYip/ohl-calcs
Licença: MIT
Dados originais: Catálogos Olex (Nexans AU) e Prysmian AU.
"""

from __future__ import annotations

import csv
import io
import time

from cablegen.models import CableEntry, CableFamily, ColumnDef
from cablegen.sources.base import DataSource

CSV_URL = (
  "https://raw.githubusercontent.com/LiaungYip/ohl-calcs/"
  "main/conductor_data/catalog_data.csv"
)

# Mapeamento de tipos do CSV para nomes de família padronizados
_TYPE_MAP = {
  "AAC": "AAC",
  "AAAC/1120": "AAAC",
  "ACSR/GZ": "ACSR",
  "ACSR/AC": "ACSR",
  "AACSR/GZ": "AACSR",
  "AACSR/AC": "AACSR",
  "HDCU": "COPPER",
  "SC/GZ": "STEEL_CORE",
  "SC/AC": "STEEL_CORE",
}


class OhlCalcsSource(DataSource):
  """Importador do CSV público do ohl-calcs."""

  @property
  def name(self) -> str:
    return "ohl_calcs"

  def available_families(self) -> list[str]:
    return ["AAC", "AAAC", "ACSR", "AACSR", "COPPER", "STEEL_CORE"]

  def _fetch_raw(self, family: str) -> list[dict]:
    import urllib.request

    req = urllib.request.Request(CSV_URL, headers={"User-Agent": "cables-td-generator/0.1"})
    with urllib.request.urlopen(req, timeout=30) as resp:
      text = resp.read().decode("utf-8", errors="replace")

    reader = csv.DictReader(io.StringIO(text))
    results: list[dict] = []
    for row in reader:
      csv_type = row.get("Type", "").strip()
      mapped = _TYPE_MAP.get(csv_type)
      if mapped and mapped.upper() == family.upper():
        results.append(dict(row))

    time.sleep(0.5)  # Rate limiting
    return results

  def _parse_entries(self, family: str, raw_data: list[dict]) -> list[CableEntry]:
    entries: list[CableEntry] = []
    seen: set[str] = set()
    for row in raw_data:
      def _f(key: str) -> float | None:
        v = row.get(key, "").strip()
        if not v:
          return None
        try:
          return float(v)
        except ValueError:
          return None

      def _i(key: str) -> int | None:
        v = _f(key)
        return int(v) if v is not None else None

      manufacturer = row.get("Manufacturer", "").strip()
      codename = row.get("Codename", "").strip()

      # Deduplicar por code_word (case-insensitive)
      key = codename.upper()
      if key in seen:
        continue
      seen.add(key)

      mass_kg_m = _f("Approximate mass (kg/m)")

      entries.append(CableEntry(
        code_word=codename.title(),
        area_total_mm2=_f("Cross sectional area (mm²)"),
        n_wires_al=_i("Cu/Al strand count (no)"),
        wire_diam_al_mm=_f("Cu/Al strand wire diameter (mm)"),
        n_wires_steel=_i("Steel strand count (no)"),
        wire_diam_steel_mm=_f("Steel strand wire diameter (mm)"),
        conductor_diameter_mm=_f("Nominal overall diameter (mm)"),
        mass_total_kg_km=mass_kg_m * 1000 if mass_kg_m is not None else None,
        rated_strength_kn=_f("Breaking load (kN)"),
        modulus_of_elasticity_gpa=_f("Modulus of elasticity (GPa)"),
        coeff_linear_expansion=_f("Coefficient of linear expansion (×10e-6/deg. C)"),
        dc_resist_20c_ohm_km=_f("DC resistance at 20 deg. C (ohm/km)"),
        ac_resist_75c_ohm_km=_f("AC resistance  at 50Hz 75 deg. C (ohm/km)"),
        source=f"ohl-calcs ({manufacturer})",
      ))
    return entries


def get_source() -> OhlCalcsSource:
  """Retorna instância do importador ohl-calcs."""
  return OhlCalcsSource()
