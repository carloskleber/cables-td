"""
Modelos de dados para cabos condutores e propriedades de materiais.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CableEntry:
  """Registro unificado de um cabo condutor.

  Todos os campos opcionais permitem que famílias diferentes
  (ex: AAC sem aço, ACSR com aço) usem o mesmo modelo.
  """

  # --- Identificação ---
  code_word: str
  alt_code: str | None = None
  size_awg_kcmil: str | None = None
  stranding: str | None = None
  country: str | None = None

  # --- Seção transversal (mm²) ---
  area_al_mm2: float | None = None
  area_steel_mm2: float | None = None
  area_alloy_mm2: float | None = None
  area_total_mm2: float | None = None

  # --- Geometria dos fios ---
  n_wires_al: int | None = None
  wire_diam_al_mm: float | None = None
  n_wires_steel: int | None = None
  wire_diam_steel_mm: float | None = None
  n_wires_alloy: int | None = None
  wire_diam_alloy_mm: float | None = None

  # --- Diâmetros do cabo ---
  core_diameter_mm: float | None = None
  conductor_diameter_mm: float | None = None

  # --- Massa (kg/km) ---
  mass_al_kg_km: float | None = None
  mass_steel_kg_km: float | None = None
  mass_total_kg_km: float | None = None

  # --- Propriedades mecânicas ---
  rated_strength_kn: float | None = None
  rated_strength_class_a_kn: float | None = None
  rated_strength_class_b_kn: float | None = None
  modulus_of_elasticity_gpa: float | None = None
  coeff_linear_expansion: float | None = None

  # --- Propriedades elétricas ---
  dc_resist_20c_ohm_km: float | None = None
  ac_resist_75c_ohm_km: float | None = None

  # --- Ampacidade (A) ---
  ampacity: dict[str, float] = field(default_factory=dict)

  # --- Metadados ---
  source: str | None = None


@dataclass
class ColumnDef:
  """Definição de uma coluna na tabela Markdown.

  Attributes:
    key: Nome do atributo em CableEntry (ou callable key).
    header: Cabeçalho exibido na tabela.
    formatter: Função para formatar o valor (opcional).
    align: Alinhamento da coluna ('left', 'center', 'right').
  """

  key: str
  header: str
  formatter: Any = None
  align: str = "left"


@dataclass
class MaterialProperty:
  """Propriedade de um material condutor."""

  material: str
  temper: str | None = None
  resistivity_ohm_m: float | None = None
  conductivity_s_m: float | None = None
  temp_coefficient: float | None = None
  conductivity_iacs_pct: float | None = None
  density_g_cm3: float | None = None
  modulus_elasticity_gpa: float | None = None
  dilatation_coefficient: float | None = None
  specific_heat_j_g_c: float | None = None
  thermal_conductivity: float | None = None
  reference: str | None = None


@dataclass
class CableFamily:
  """Define uma família de cabos (ex: ACSR, AAC, etc.).

  Cada família produz um arquivo .md separado.
  """

  name: str
  description: str
  description_pt: str | None = None
  output_filename: str = ""
  columns: list[ColumnDef] = field(default_factory=list)
  entries: list[CableEntry] = field(default_factory=list)
  references: list[str] = field(default_factory=list)
  standard: str | None = None

  def __post_init__(self) -> None:
    if not self.output_filename:
      self.output_filename = f"{self.name}.md"
