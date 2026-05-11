"""
Render the traditional cable catalog Markdown files.
"""

from __future__ import annotations

from pathlib import Path

from cablegen.data.material_properties import MATERIALS, REFERENCES
from cablegen.models import CableFamily
from cablegen.catalog_base_renderer import (
  _extract_value,
  _format_value,
  render_family,
  render_material_properties,
)

from cablegen.renderer import write_output


def render_catalog_files(
  families: list[CableFamily],
  output_dir: Path,
  dry_run: bool = False,
  no_materials: bool = False,
) -> None:
  """Render one Markdown file per family, matching the original cablegen output."""
  for family in families:
    content = _render_any_family(family)
    write_output(content, output_dir / family.output_filename, dry_run)

  if not no_materials:
    content = render_material_properties(MATERIALS, REFERENCES)
    write_output(content, output_dir / "material_properties.md", dry_run)


def _render_any_family(family: CableFamily) -> str:
  name_upper = family.name.upper().replace(" ", "_")
  if name_upper == "ACSR":
    return _render_acsr_astm(family)
  if name_upper == "ACSR_EN":
    return _render_acsr_en(family)
  return render_family(family)


def _render_acsr_astm(family: CableFamily) -> str:
  parts: list[str] = []
  parts.append(f"# {family.name} - {family.description}")
  parts.append("")
  if family.description_pt:
    parts.append(f"({family.description_pt})")
    parts.append("")

  cols = family.columns
  header = "| " + " | ".join(c.header for c in cols) + " |"
  sep = "| " + " | ".join("-" * max(3, len(c.header)) for c in cols) + " |"
  parts.append(header)
  parts.append(sep)

  for entry in family.entries:
    cells: list[str] = []
    for col in cols:
      if col.key == "_area":
        a = f"{entry.area_al_mm2:g}" if entry.area_al_mm2 else ""
        s = f"{entry.area_steel_mm2:g}" if entry.area_steel_mm2 else ""
        cells.append(f"{a} / {s}" if a and s else "")
      elif col.key == "_wires_al":
        if entry.n_wires_al and entry.wire_diam_al_mm:
          cells.append(f"{entry.n_wires_al} x {entry.wire_diam_al_mm:.2f}")
        else:
          cells.append("")
      elif col.key == "_wires_steel":
        if entry.n_wires_steel and entry.wire_diam_steel_mm:
          cells.append(f"{entry.n_wires_steel} x {entry.wire_diam_steel_mm:.2f}")
        else:
          cells.append("")
      else:
        val = _extract_value(entry, col.key)
        cells.append(_format_value(val, col.formatter))
    parts.append("| " + " | ".join(cells) + " |")

  parts.append("")
  if family.references:
    parts.append("References:")
    parts.append("")
    for ref in family.references:
      parts.append(f"* {ref}")
    parts.append("")
  return "\n".join(parts)


def _render_acsr_en(family: CableFamily) -> str:
  from cablegen.data.acsr_en import (
    _fmt_areas,
    _fmt_diameters,
    _fmt_n_wires,
    _fmt_wire_diam,
  )

  parts: list[str] = []
  parts.append(f"# {family.name} - {family.description}")
  parts.append("")
  if family.description_pt:
    parts.append(f"({family.description_pt})")
    parts.append("")

  cols = family.columns
  header = "| " + " | ".join(c.header for c in cols) + " |"
  sep = "| " + " | ".join("-" * max(3, len(c.header)) for c in cols) + " |"
  parts.append(header)
  parts.append(sep)

  for entry in family.entries:
    cells: list[str] = []
    for col in cols:
      if col.key == "_areas":
        cells.append(_fmt_areas(entry))
      elif col.key == "_n_wires":
        cells.append(_fmt_n_wires(entry))
      elif col.key == "_wire_diam":
        cells.append(_fmt_wire_diam(entry))
      elif col.key == "_diameters":
        cells.append(_fmt_diameters(entry))
      else:
        val = _extract_value(entry, col.key)
        cells.append(_format_value(val, col.formatter))
    parts.append("| " + " | ".join(cells) + " |")

  parts.append("")
  if family.references:
    parts.append("References:")
    parts.append("")
    for ref in family.references:
      parts.append(f"* {ref}")
    parts.append("")
  return "\n".join(parts)
