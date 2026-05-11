"""
Definições de colunas padrão para cada tipo de família de cabos.

Quando dados são importados de fontes online e não há colunas definidas,
este módulo fornece colunas adequadas automaticamente, adaptando-se
à presença ou ausência de campos (ex: cabos sem aço).
"""

from __future__ import annotations

from cablegen.models import ColumnDef

# Famílias que possuem reforço de aço
_STEEL_FAMILIES = {"ACSR", "AACSR", "ACSR_AW", "ACSR_TW", "ACSS", "ACSS_AW", "ACSS_TW", "STEEL_CORE"}

# Famílias de alumínio puro
_AL_ONLY_FAMILIES = {"AAC", "AAAC", "AAC_TW"}

# Famílias com liga de alumínio reforçada
_ALLOY_REINFORCED_FAMILIES = {"ACAR"}

# Famílias de cobre
_COPPER_FAMILIES = {"COPPER", "HDCU"}


def _base_columns() -> list[ColumnDef]:
  """Colunas comuns a todas as famílias."""
  return [
    ColumnDef(key="code_word", header="Code word"),
    ColumnDef(key="area_total_mm2", header="Area (mm²)", align="right"),
    ColumnDef(key="conductor_diameter_mm", header="Diameter (mm)", align="right"),
    ColumnDef(key="mass_total_kg_km", header="Mass (kg/km)", align="right"),
    ColumnDef(key="rated_strength_kn", header="Rated strength (kN)", align="right"),
    ColumnDef(key="dc_resist_20c_ohm_km", header="DC resist. 20°C (Ω/km)", align="right"),
    ColumnDef(key="ac_resist_75c_ohm_km", header="AC resist. 75°C (Ω/km)", align="right"),
  ]


def _al_stranding_columns() -> list[ColumnDef]:
  """Colunas de encordoamento de alumínio."""
  return [
    ColumnDef(key="n_wires_al", header="Al wires", align="right"),
    ColumnDef(key="wire_diam_al_mm", header="Al wire ø (mm)", align="right"),
  ]


def _steel_stranding_columns() -> list[ColumnDef]:
  """Colunas de encordoamento de aço."""
  return [
    ColumnDef(key="n_wires_steel", header="Steel wires", align="right"),
    ColumnDef(key="wire_diam_steel_mm", header="Steel wire ø (mm)", align="right"),
  ]


def _elasticity_columns() -> list[ColumnDef]:
  """Colunas de propriedades mecânicas adicionais."""
  return [
    ColumnDef(key="modulus_of_elasticity_gpa", header="E (GPa)", align="right"),
    ColumnDef(key="coeff_linear_expansion", header="α (×10⁻⁶/°C)", align="right"),
  ]


# Descrições padrão por família
FAMILY_DESCRIPTIONS: dict[str, tuple[str, str]] = {
  "AAC": (
    "All Aluminum Conductor",
    "Cabos de alumínio puro",
  ),
  "AAAC": (
    "All Aluminum Alloy Conductor",
    "Cabos de liga de alumínio",
  ),
  "ACAR": (
    "Aluminum Conductor, Alloy Reinforced",
    "Cabos de alumínio com reforço de liga",
  ),
  "ACSR": (
    "Aluminum Conductor, Steel Reinforced",
    "CAA - Cabos de alumínio com alma de aço",
  ),
  "AACSR": (
    "Aluminum Alloy Conductor, Steel Reinforced",
    "Cabos de liga de alumínio com alma de aço",
  ),
  "ACSR_AW": (
    "Aluminum Conductor, Aluminum-Clad Steel Reinforced",
    "CAA com aço revestido de alumínio",
  ),
  "ACSR_TW": (
    "Aluminum Conductor, Steel Reinforced, Trapezoidal Wire",
    "CAA com fio trapezoidal",
  ),
  "ACSS": (
    "Aluminum Conductor, Steel Supported",
    "Cabos de alumínio com suporte de aço",
  ),
  "ACSS_AW": (
    "Aluminum Conductor, Aluminum-Clad Steel Supported",
    "Cabos de alumínio com suporte de aço revestido",
  ),
  "ACSS_TW": (
    "Aluminum Conductor, Steel Supported, Trapezoidal Wire",
    "Cabos de alumínio com suporte de aço - fio trapezoidal",
  ),
  "COPPER": (
    "Bare Copper Conductor",
    "Cabos de cobre nu",
  ),
  "HDCU": (
    "Hard-Drawn Copper Conductor",
    "Cabos de cobre duro",
  ),
  "STEEL_CORE": (
    "Steel Core Wire",
    "Fios de aço para alma de cabos",
  ),
}


def get_default_columns(family_name: str) -> list[ColumnDef]:
  """Retorna colunas padrão para uma família de cabos.

  Adapta automaticamente as colunas com base no tipo da família:
  - Famílias com aço: inclui colunas de encordoamento Al + Steel
  - Famílias só alumínio: inclui colunas de encordoamento Al
  - Todas: inclui colunas de propriedades mecânicas/elétricas
  """
  key = family_name.upper().replace(" ", "_").replace("/", "_")

  cols: list[ColumnDef] = [
    ColumnDef(key="code_word", header="Code word"),
  ]

  # Colunas de encordoamento
  cols.extend(_al_stranding_columns())

  if key in _STEEL_FAMILIES:
    cols.extend(_steel_stranding_columns())

  # Colunas de geometria e massa
  cols.extend([
    ColumnDef(key="area_total_mm2", header="Area (mm²)", align="right"),
    ColumnDef(key="conductor_diameter_mm", header="Diameter (mm)", align="right"),
    ColumnDef(key="mass_total_kg_km", header="Mass (kg/km)", align="right"),
  ])

  # Propriedades mecânicas
  cols.append(ColumnDef(key="rated_strength_kn", header="Rated strength (kN)", align="right"))
  cols.extend(_elasticity_columns())

  # Propriedades elétricas
  cols.extend([
    ColumnDef(key="dc_resist_20c_ohm_km", header="DC resist. 20°C (Ω/km)", align="right"),
    ColumnDef(key="ac_resist_75c_ohm_km", header="AC resist. 75°C (Ω/km)", align="right"),
  ])

  return cols


def get_family_description(family_name: str) -> tuple[str, str | None]:
  """Retorna (description_en, description_pt) para uma família."""
  key = family_name.upper().replace(" ", "_").replace("/", "_")
  desc = FAMILY_DESCRIPTIONS.get(key)
  if desc:
    return desc
  return (family_name, None)
