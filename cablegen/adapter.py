"""
Adapter between cablegen cable entries and pandapower line std_types.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import fields
from typing import Iterable, Any

from cablegen.data import get_all_families
from cablegen.columns import get_default_columns, get_family_description
from cablegen.models import CableEntry, CableFamily


@dataclass(frozen=True)
class LineTypeAssumptions:
  """Electrical assumptions needed by pandapower but absent from catalogs."""

  x_ohm_per_km: float = 0.4
  c_nf_per_km: float = 10.0
  default_max_i_ka: float = 1.0
  alpha: float = 0.00403
  line_type: str = "ol"


def load_families(
  family_filter: str | None = None,
  include_sources: bool = True,
  source_name: str | None = None,
  refresh: bool = False,
) -> list[CableFamily]:
  """Load built-in families plus cached or refreshed source data."""
  families = get_all_families()
  if include_sources:
    families = merge_source_families(
      families,
      source_name=source_name,
      refresh=refresh,
    )

  if family_filter is None:
    return families

  key = _normalize_key(family_filter)
  selected = [
    family for family in families
    if key in _family_keys(family)
  ]
  if not selected:
    names = ", ".join(f.name for f in families)
    raise ValueError(f"Família '{family_filter}' não encontrada. Disponíveis: {names}")
  return selected


def merge_source_families(
  families: list[CableFamily],
  source_name: str | None = None,
  refresh: bool = False,
) -> list[CableFamily]:
  """Merge cached or refreshed source data with the provided families."""
  result = list(families)
  sources = get_sources()
  if source_name:
    if source_name not in sources:
      available = ", ".join(sources)
      raise ValueError(f"Fonte '{source_name}' não encontrada. Disponíveis: {available}")
    sources = {source_name: sources[source_name]}

  for name, source in sources.items():
    mode = "refresh" if refresh else "cache"
    print(f"Fonte: {name} ({mode})")
    for family_name in source.available_families():
      entries = _load_source_entries(source, family_name, refresh=refresh)
      if not entries:
        continue

      desc_en, desc_pt = get_family_description(family_name)
      imported = CableFamily(
        name=family_name,
        description=desc_en,
        description_pt=desc_pt,
        columns=get_default_columns(family_name),
        entries=entries,
        references=[f"Source: {name}"],
      )
      _merge_family(result, imported)
      print(f"  {family_name}: {len(entries)} entradas importadas")

  return result


def _load_source_entries(source: Any, family_name: str, refresh: bool) -> list[CableEntry]:
  if refresh:
    return source.fetch(family_name, force=True)

  cache_key = f"{source.name}_{family_name}"
  raw = source._read_cache(cache_key)
  if raw is None:
    print(f"  {family_name}: sem cache local")
    return []
  print(f"  Cache hit: {source.name}/{family_name}")
  return source._parse_entries(family_name, raw)


def get_sources() -> dict[str, Any]:
  """Return online/cache-backed data sources available to cablegen."""
  sources: dict[str, Any] = {}
  try:
    from cablegen.sources.ohl_calcs import get_source as get_ohl
    sources["ohl_calcs"] = get_ohl()
  except ImportError:
    pass
  try:
    from cablegen.sources.champwire import get_source as get_champwire
    sources["champwire"] = get_champwire()
  except ImportError:
    pass
  try:
    from cablegen.sources.priority_wire import get_source as get_priority_wire
    sources["priority_wire"] = get_priority_wire()
  except ImportError:
    pass
  return sources


def create_catalog_network(
  families: Iterable[CableFamily] | None = None,
  assumptions: LineTypeAssumptions | None = None,
  overwrite: bool = True,
) -> Any:
  """Create an empty pandapower net and register cable entries as line std_types."""
  pp = _require_pandapower()
  net = pp.create_empty_network()
  register_line_types(net, families or load_families(), assumptions, overwrite=overwrite)
  return net


def register_line_types(
  net: Any,
  families: Iterable[CableFamily],
  assumptions: LineTypeAssumptions | None = None,
  overwrite: bool = True,
) -> int:
  """Register cable entries as pandapower line standard types."""
  pp = _require_pandapower()
  assumptions = assumptions or LineTypeAssumptions()
  count = 0

  for family in families:
    used_names: set[str] = set()
    for entry in family.entries:
      converted = entry_to_std_type(family, entry, assumptions)
      if converted is None:
        continue

      name, data = converted
      name = _unique_name(name, used_names)
      used_names.add(name)
      pp.create_std_type(
        net,
        data,
        name,
        element="line",
        overwrite=overwrite,
        check_required=True,
      )
      count += 1

  return count


def entry_to_std_type(
  family: CableFamily,
  entry: CableEntry,
  assumptions: LineTypeAssumptions,
) -> tuple[str, dict[str, object]] | None:
  """Convert a cable entry to a pandapower line std_type tuple."""
  r_ohm_per_km = _positive(entry.dc_resist_20c_ohm_km)
  if r_ohm_per_km is None:
    return None

  q_mm2 = _area_mm2(entry)
  name = _line_type_name(family, entry)
  data: dict[str, object] = {
    "r_ohm_per_km": r_ohm_per_km,
    "x_ohm_per_km": assumptions.x_ohm_per_km,
    "c_nf_per_km": assumptions.c_nf_per_km,
    "max_i_ka": _max_i_ka(entry, assumptions),
    "type": assumptions.line_type,
    "alpha": assumptions.alpha,
    "family": family.name,
    "code_word": entry.code_word or entry.alt_code or name,
    "source": entry.source or "",
  }

  for field in fields(entry):
    value = getattr(entry, field.name)
    if value is not None and value != {}:
      data[f"cg_{field.name}"] = value

  optional_values = {
    "q_mm2": q_mm2,
    "diameter_mm": entry.conductor_diameter_mm,
    "mass_kg_per_km": entry.mass_total_kg_km,
    "rated_strength_kn": (
      entry.rated_strength_kn
      or entry.rated_strength_class_a_kn
      or entry.rated_strength_class_b_kn
    ),
    "stranding": entry.stranding,
    "size_awg_kcmil": entry.size_awg_kcmil,
    "standard": family.standard,
  }
  data.update({k: v for k, v in optional_values.items() if v is not None})
  return name, data


def available_line_types(net: Any) -> Any:
  """Return pandapower's line std_type table for a network."""
  pp = _require_pandapower()
  return pp.available_std_types(net, element="line")


def catalog_line_types(net: Any) -> Any:
  """Return only line std_types generated by cablegen."""
  table = available_line_types(net)
  if "family" not in table.columns:
    return table.iloc[0:0].copy()
  return table[table["family"].notna()].copy()


def _require_pandapower() -> Any:
  try:
    import pandapower as pp
  except ImportError as exc:
    raise RuntimeError(
      "pandapower não está instalado. Instale com `pip install -r requirements.txt`."
    ) from exc
  return pp


def _area_mm2(entry: CableEntry) -> float | None:
  values = [
    entry.area_total_mm2,
    _sum_optional(entry.area_al_mm2, entry.area_steel_mm2),
    _sum_optional(entry.area_al_mm2, entry.area_alloy_mm2),
    entry.area_al_mm2,
    entry.area_alloy_mm2,
  ]
  for value in values:
    if value is not None and value > 0:
      return value
  return None


def _max_i_ka(entry: CableEntry, assumptions: LineTypeAssumptions) -> float:
  if entry.ampacity:
    return max(entry.ampacity.values()) / 1000
  return assumptions.default_max_i_ka


def _positive(value: float | None) -> float | None:
  if value is None or value <= 0:
    return None
  return value


def _sum_optional(*values: float | None) -> float | None:
  present = [value for value in values if value is not None]
  if not present:
    return None
  return sum(present)


def _line_type_name(family: CableFamily, entry: CableEntry) -> str:
  code = entry.code_word or entry.alt_code or entry.size_awg_kcmil or "unnamed"
  suffix = f" {entry.stranding}" if entry.stranding else ""
  return f"{family.name} {code}{suffix}".strip()


def _unique_name(name: str, used_names: set[str]) -> str:
  if name not in used_names:
    return name
  i = 2
  while f"{name} ({i})" in used_names:
    i += 1
  return f"{name} ({i})"


def _normalize_key(value: str) -> str:
  return value.upper().replace(" ", "_").replace("/", "_").replace("-", "_")


def _family_keys(family: CableFamily) -> set[str]:
  output_stem = family.output_filename.rsplit(".", 1)[0]
  return {_normalize_key(family.name), _normalize_key(output_stem)}


def _merge_family(families: list[CableFamily], imported: CableFamily) -> None:
  existing = _find_equivalent_family(families, imported.name)
  if existing is None:
    families.append(imported)
    return

  existing_entries = {
    _entry_key(entry): entry
    for entry in existing.entries
  }
  for new_entry in imported.entries:
    key = _entry_key(new_entry)
    old_entry = existing_entries.get(key)
    if old_entry is None:
      existing.entries.append(new_entry)
      existing_entries[key] = new_entry
    else:
      _backfill_entry(old_entry, new_entry)

  refs = set(existing.references)
  for ref in imported.references:
    if ref not in refs:
      existing.references.append(ref)


def _find_equivalent_family(families: list[CableFamily], family_name: str) -> CableFamily | None:
  key = _normalize_key(family_name)
  for family in families:
    if key in _family_keys(family):
      return family
  return None


def _entry_key(entry: CableEntry) -> str:
  parts = [
    entry.code_word or entry.alt_code or "",
    entry.size_awg_kcmil or "",
    entry.stranding or "",
  ]
  return "|".join(_normalize_key(part) for part in parts)


def _backfill_entry(existing: CableEntry, new_entry: CableEntry) -> None:
  for field in fields(CableEntry):
    name = field.name
    if name in {"code_word", "alt_code", "source"}:
      continue
    if getattr(existing, name) in (None, {}) and getattr(new_entry, name) not in (None, {}):
      setattr(existing, name, getattr(new_entry, name))
