"""
Markdown rendering for pandapower std_type tables.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cablegen.models import CableFamily

from cablegen.adapter import LineTypeAssumptions


DEFAULT_COLUMNS = [
  "family",
  "code_word",
  "r_ohm_per_km",
  "x_ohm_per_km",
  "c_nf_per_km",
  "max_i_ka",
  "type",
  "q_mm2",
  "diameter_mm",
  "mass_kg_per_km",
  "rated_strength_kn",
  "stranding",
  "source",
]


def render_line_types_markdown(
  table: Any,
  families: list[CableFamily],
  assumptions: LineTypeAssumptions,
) -> str:
  """Render a pandapower std_type dataframe as Markdown."""
  selected = _select_columns(table, DEFAULT_COLUMNS)
  rows = _dataframe_rows(selected)

  parts: list[str] = [
    "# pandapower line standard types",
    "",
    "Generated from the local cable catalog using pandapower standard types.",
    "",
    "Families:",
  ]
  for family in families:
    parts.append(f"- {family.name}: {len(family.entries)} catalog entries")

  parts.extend([
    "",
    "Assumptions for fields not present in the source catalogs:",
    f"- x_ohm_per_km: {assumptions.x_ohm_per_km:g}",
    f"- c_nf_per_km: {assumptions.c_nf_per_km:g}",
    f"- default max_i_ka: {assumptions.default_max_i_ka:g}",
    f"- alpha: {assumptions.alpha:g}",
    "",
  ])
  parts.append(_render_markdown_table(selected.columns, rows))
  parts.append("")
  return "\n".join(parts)


def write_output(content: str, path: Path, dry_run: bool = False) -> None:
  """Write Markdown output or print it in dry-run mode."""
  if dry_run:
    print(f"--- {path} ---")
    print(content)
    return
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(content, encoding="utf-8")
  print(f"  OK {path}")


def _select_columns(table: Any, columns: list[str]) -> Any:
  present = [col for col in columns if col in table.columns]
  return table[present].copy()


def _dataframe_rows(table: Any) -> list[list[str]]:
  rows: list[list[str]] = []
  for index, row in table.iterrows():
    values = [str(index)]
    for col in table.columns:
      values.append(_format_cell(row[col]))
    rows.append(values)
  return rows


def _render_markdown_table(columns: Any, rows: list[list[str]]) -> str:
  headers = ["std_type"] + [str(col) for col in columns]
  separator = ["-" * max(3, len(header)) for header in headers]
  lines = [
    "| " + " | ".join(headers) + " |",
    "| " + " | ".join(separator) + " |",
  ]
  for row in rows:
    lines.append("| " + " | ".join(_escape_markdown(value) for value in row) + " |")
  return "\n".join(lines)


def _format_cell(value: object) -> str:
  if value is None:
    return ""
  try:
    if value != value:
      return ""
  except TypeError:
    pass
  if isinstance(value, float):
    return f"{value:g}"
  return str(value)


def _escape_markdown(value: str) -> str:
  return value.replace("|", "\\|")
