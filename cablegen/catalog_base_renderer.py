"""
Renderizador de tabelas Markdown para famílias de cabos.
"""

from __future__ import annotations

from pathlib import Path

from cablegen.models import (
  CableEntry,
  CableFamily,
  ColumnDef,
  MaterialProperty,
)


def _format_value(value: object, formatter: object = None) -> str:
  """Formata um valor para exibição na tabela Markdown."""
  if value is None:
    return ""
  if formatter is not None:
    return formatter(value)
  if isinstance(value, float):
    # Remove zeros desnecessários, mas mantém precisão
    s = f"{value:g}"
    return s
  return str(value)


def _extract_value(entry: CableEntry, key: str) -> object:
  """Extrai valor de um CableEntry por chave, suportando chaves compostas."""
  if "." in key:
    parts = key.split(".", 1)
    obj = getattr(entry, parts[0], None)
    if obj is None:
      return None
    if isinstance(obj, dict):
      return obj.get(parts[1])
    return getattr(obj, parts[1], None)
  return getattr(entry, key, None)


def render_table(columns: list[ColumnDef], entries: list[CableEntry]) -> str:
  """Renderiza uma tabela Markdown a partir de colunas e entradas.

  Returns:
    String com a tabela formatada em Markdown.
  """
  if not columns:
    return ""

  # Cabeçalho
  header_row = "| " + " | ".join(col.header for col in columns) + " |"

  # Separador com alinhamento
  sep_parts: list[str] = []
  for col in columns:
    if col.align == "center":
      sep_parts.append(":" + "-" * max(3, len(col.header) - 2) + ":")
    elif col.align == "right":
      sep_parts.append("-" * max(3, len(col.header) - 1) + ":")
    else:
      sep_parts.append("-" * max(3, len(col.header)))
  separator_row = "| " + " | ".join(sep_parts) + " |"

  # Linhas de dados
  data_rows: list[str] = []
  for entry in entries:
    cells: list[str] = []
    for col in columns:
      raw_value = _extract_value(entry, col.key)
      cells.append(_format_value(raw_value, col.formatter))
    row = "| " + " | ".join(cells) + " |"
    data_rows.append(row)

  lines = [header_row, separator_row] + data_rows
  return "\n".join(lines)


def render_family(family: CableFamily) -> str:
  """Renderiza uma família de cabos completa como Markdown.

  Inclui título, subtítulo em PT-BR, tabela e referências.
  """
  parts: list[str] = []

  # Título
  parts.append(f"# {family.name} - {family.description}")
  parts.append("")

  # Subtítulo em português
  if family.description_pt:
    parts.append(f"({family.description_pt})")
    parts.append("")

  # Tabela
  if family.columns and family.entries:
    parts.append(render_table(family.columns, family.entries))
    parts.append("")

  # Referências
  if family.references:
    parts.append("References:")
    parts.append("")
    for ref in family.references:
      parts.append(f"* {ref}")
    parts.append("")

  return "\n".join(parts)


def render_material_properties(
  materials: list[MaterialProperty],
  references: list[str],
) -> str:
  """Renderiza a tabela de propriedades de materiais como Markdown."""
  parts: list[str] = []
  parts.append("# Material properties")
  parts.append("")

  # Cabeçalho fixo conforme formato existente
  headers = [
    "Material",
    "Temper (hardness)",
    "Resistivity @ 20°C, Ω m",
    "Conductivity @ 20°C, S/m",
    "Temperature coefficient, 1/°C",
    "Conductivity % IACS",
    "Density @ 20°C, g/cm³",
    "Modulus of elasticity, Gpa",
    "Dilatation coefficient, 1/°C",
    "Specific heat, J/g °C",
    "Thermal conductivity, cal/cm s °C",
    "Reference",
  ]

  header_row = "| " + " | ".join(headers) + " |"
  separator_row = "| " + " | ".join("-" * max(3, len(h)) for h in headers) + " |"

  parts.append(header_row)
  parts.append(separator_row)

  def _fmt_sci(v: float | None) -> str:
    if v is None:
      return ""
    # Formato científico com 3 casas decimais
    return f"{v:.3E}"

  def _fmt_num(v: float | None) -> str:
    if v is None:
      return ""
    return f"{v:g}"

  for mat in materials:
    cells = [
      mat.material,
      mat.temper or "",
      _fmt_sci(mat.resistivity_ohm_m),
      _fmt_sci(mat.conductivity_s_m),
      _fmt_sci(mat.temp_coefficient),
      _fmt_num(mat.conductivity_iacs_pct),
      _fmt_num(mat.density_g_cm3),
      _fmt_num(mat.modulus_elasticity_gpa) if mat.modulus_elasticity_gpa else "",
      _fmt_sci(mat.dilatation_coefficient) if mat.dilatation_coefficient else "",
      _fmt_num(mat.specific_heat_j_g_c) if mat.specific_heat_j_g_c else "",
      _fmt_num(mat.thermal_conductivity) if mat.thermal_conductivity else "",
      mat.reference or "",
    ]
    parts.append("| " + " | ".join(cells) + " |")

  parts.append("")

  # Referências
  if references:
    parts.append("References:")
    parts.append("")
    for ref in references:
      parts.append(f"* {ref}")
    parts.append("")

  return "\n".join(parts)


def write_output(content: str, filepath: Path, dry_run: bool = False) -> None:
  """Escreve conteúdo em arquivo ou stdout (dry-run)."""
  if dry_run:
    print(f"--- {filepath} ---")
    print(content)
    print()
  else:
    filepath.write_text(content, encoding="utf-8")
    print(f"  OK {filepath}")
