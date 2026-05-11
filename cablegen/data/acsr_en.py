"""
Dados pré-definidos: ACSR padrão EN (BS EN 50182).
"""

from cablegen.models import CableEntry, CableFamily, ColumnDef


def _fmt_areas(entry: CableEntry) -> str:
  """Formata áreas Al/Steel/Total."""
  parts = []
  if entry.area_al_mm2 is not None:
    parts.append(f"{entry.area_al_mm2:g}")
  if entry.area_steel_mm2 is not None:
    parts.append(f"{entry.area_steel_mm2:g}")
  if entry.area_total_mm2 is not None:
    parts.append(f"{entry.area_total_mm2:g}")
  return " / ".join(parts) if parts else ""


def _fmt_n_wires(entry: CableEntry) -> str:
  """Formata número de fios Al/Steel."""
  parts = []
  if entry.n_wires_al is not None:
    parts.append(str(entry.n_wires_al))
  if entry.n_wires_steel is not None:
    parts.append(str(entry.n_wires_steel))
  return " / ".join(parts) if parts else ""


def _fmt_wire_diam(entry: CableEntry) -> str:
  """Formata diâmetro de fios Al/Steel."""
  parts = []
  if entry.wire_diam_al_mm is not None:
    parts.append(f"{entry.wire_diam_al_mm:.2f}")
  if entry.wire_diam_steel_mm is not None:
    parts.append(f"{entry.wire_diam_steel_mm:.2f}")
  return " / ".join(parts) if parts else ""


def _fmt_diameters(entry: CableEntry) -> str:
  """Formata diâmetro Core/Cond."""
  parts = []
  if entry.core_diameter_mm is not None:
    parts.append(f"{entry.core_diameter_mm:g}")
  if entry.conductor_diameter_mm is not None:
    parts.append(f"{entry.conductor_diameter_mm:g}")
  return " / ".join(parts) if parts else ""


# Colunas customizadas para ACSR EN
COLUMNS = [
  ColumnDef(key="country", header="Country"),
  ColumnDef(key="code_word", header="Code"),
  ColumnDef(key="alt_code", header="Old code"),
  ColumnDef(key="_areas", header="Areas Al/Steel/Total (mm²)"),
  ColumnDef(key="_n_wires", header="No. of wires Al/Steel"),
  ColumnDef(key="_wire_diam", header="Wire diameter Al/Steel (mm)"),
  ColumnDef(key="_diameters", header="Diameter Core/Cond. (mm)"),
  ColumnDef(key="mass_total_kg_km", header="Mass (kg/km)"),
  ColumnDef(key="rated_strength_kn", header="Rated strength (kN)"),
  ColumnDef(key="dc_resist_20c_ohm_km", header="DC resist. (Ω/km)"),
]

# fmt: off
_RAW = [
  ("GB","11-AL1/2-ST1A","MOLE",10.6,1.77,12.4,6,1,1.50,1.50,1.50,4.50,42.8,4.14,2.7027),
  ("GB","21-AL1/3-ST1A","SQUIRREL",21.0,3.50,24.5,6,1,2.11,2.11,2.11,6.33,84.7,7.87,1.3659),
  ("GB","26-AL1/4-ST1A","GOPHER",26.2,4.37,30.6,6,1,2.36,2.36,2.36,7.08,106.0,9.58,1.0919),
  ("GB","32-AL1/5-ST1A","WEASEL",31.6,5.27,36.9,6,1,2.59,2.59,2.59,7.77,127.6,11.38,0.9065),
  ("GB","37-AL1/6-ST1A","FOX",36.7,6.11,42.8,6,1,2.79,2.79,2.79,8.37,148.1,13.21,0.7812),
  ("GB","42-AL1/7-ST1A","FERRET",42.4,7.07,49.5,6,1,3.00,3.00,3.00,9.00,171.2,15.27,0.6757),
  ("GB","53-AL1/9-ST1A","RABBIT",52.9,8.81,61.7,6,1,3.35,3.35,3.35,10.1,213.5,18.42,0.5419),
  ("GB","63-AL1/11-ST1A","MINK",63.1,10.5,73.6,6,1,3.66,3.66,3.66,11.0,254.9,21.67,0.454),
  ("GB","63-AL1/37-ST1A","SKUNK",63.2,36.9,100.1,12,7,2.59,2.59,7.77,13.0,463.0,52.79,0.4568),
  ("GB","75-AL1/13-ST1A","BEAVER",75.0,12.5,87.5,6,1,3.99,3.99,3.99,12.0,302.9,25.76,0.382),
  ("GB","73-AL1/43-ST1A","HORSE",73.4,42.8,116.2,12,7,2.79,2.79,8.37,14.0,537.3,61.25,0.3936),
  ("GB","79-AL1/13-ST1A","RACOON",78.8,13.1,92.0,6,1,4.09,4.09,4.09,12.3,318.3,27.06,0.3635),
  ("GB","84-AL1/14-ST1A","OTTER",83.9,14.0,97.9,6,1,4.22,4.22,4.22,12.7,338.8,28.81,0.3415),
  ("GB","95-AL1/16-ST1A","CAT",95.4,15.9,111.3,6,1,4.50,4.50,4.50,13.5,385.3,32.76,0.3003),
  ("GB","105-AL1/17-ST1A","HARE",105.0,17.5,122.5,6,1,4.72,4.72,4.72,14.2,423.8,36.04,0.273),
  ("GB","105-AL1/14-ST1A","DOG",105.0,13.6,118.5,6,7,4.72,1.57,4.71,14.2,394.0,32.65,0.2733),
  ("GB","132-AL1/20-ST1A","COYOTE",131.7,20.1,151.8,26,7,2.54,1.91,5.73,15.9,520.7,45.86,0.2192),
  ("GB","132-AL1/7-ST1A","COUGAR",131.5,7.31,138.8,18,1,3.05,3.05,3.05,15.3,418.8,29.74,0.2188),
  ("GB","131-AL1/31-ST1A","TIGER",131.2,30.6,161.9,30,7,2.36,2.36,7.08,16.5,602.2,57.87,0.2202),
  ("GB","158-AL1/37-ST1A","WOLF",158.1,36.9,194.9,30,7,2.59,2.59,7.77,18.1,725.3,68.91,0.1829),
  ("GB","159-AL1/9-ST1A","DINGO",158.7,8.81,167.5,18,1,3.35,3.35,3.35,16.8,505.2,35.87,0.1814),
  ("GB","183-AL1/43-ST1A","LYNX",183.4,42.8,226.2,30,7,2.79,2.79,8.37,19.5,841.6,79.97,0.1576),
  ("GB","184-AL1/10-ST1A","CARACAL",184.2,10.2,194.5,18,1,3.61,3.61,3.61,18.1,586.7,40.74,0.1562),
  ("GB","212-AL1/49-ST1A","PANTHER",212.1,49.5,261.5,30,7,3.00,3.00,9.00,21.0,973.1,92.46,0.1363),
  ("GB","211-AL1/12-ST1A","JAGUAR",210.6,11.7,222.3,18,1,3.86,3.86,3.86,19.3,670.8,46.57,0.1366),
  ("GB","238-AL1/56-ST1A","LION",238.3,55.6,293.9,30,7,3.18,3.18,9.54,22.3,1093.4,100.47,0.1213),
  ("GB","264-AL1/62-ST1A","BEAR",264.4,61.7,326.1,30,7,3.35,3.35,10.1,23.5,1213.4,111.5,0.1093),
  ("GB","324-AL1/76-ST1A","GOAT",324.3,75.7,400.0,30,7,3.71,3.71,11.1,26.0,1488.2,135.13,0.0891),
  ("GB","375-AL1/88-ST1A","SHEEP",375.1,87.5,462.6,30,7,3.99,3.99,12.0,27.9,1721.3,156.3,0.0771),
  ("GB","374-AL1/48-ST1A","ANTELOPE",374.1,48.5,422.6,54,7,2.97,2.97,8.91,26.7,1413.8,118.88,0.0773),
  ("GB","382-AL1/49-ST1A","BISON",381.7,49.5,431.2,54,7,3.00,3.00,9.00,27.0,1442.5,121.3,0.0758),
  ("GB","430-AL1/100-ST1A","DEER",429.6,100.2,529.8,30,7,4.27,4.27,12.8,29.9,1971.4,179,0.0673),
  ("GB","429-AL1/56-ST1A","ZEBRA",428.9,55.6,484.5,54,7,3.18,3.18,9.54,28.6,1620.8,131.92,0.0674),
  ("GB","477-AL1/111-ST1A","ELK",477.1,111.3,588.5,30,7,4.50,4.50,13.5,31.5,2189.5,198.8,0.0606),
  ("GB","476-AL1/62-ST1A","CAMEL",476.0,61.7,537.7,54,7,3.35,3.35,10.1,30.2,1798.8,146.4,0.0608),
  ("GB","528-AL1/69-ST1A","MOOSE",528.5,68.5,597.0,54,7,3.53,3.53,10.6,31.8,1997.3,159.92,0.0547),
]
# fmt: on


def _build_entries() -> list[CableEntry]:
  entries = []
  for r in _RAW:
    entries.append(CableEntry(
      country=r[0], code_word=r[1], alt_code=r[2],
      area_al_mm2=r[3], area_steel_mm2=r[4], area_total_mm2=r[5],
      n_wires_al=r[6], n_wires_steel=r[7],
      wire_diam_al_mm=r[8], wire_diam_steel_mm=r[9],
      core_diameter_mm=r[10], conductor_diameter_mm=r[11],
      mass_total_kg_km=r[12], rated_strength_kn=r[13],
      dc_resist_20c_ohm_km=r[14],
      source="BS EN 50182",
    ))
  return entries


def get_family() -> CableFamily:
  """Retorna a família ACSR EN com todos os dados."""
  return CableFamily(
    name="ACSR_EN",
    description="Aluminum Conductor, Steel Reinforced (EN series)",
    description_pt="CAA - Cabos de alumínio com alma de aço - padrão EN",
    output_filename="ACSR_EN.md",
    columns=COLUMNS,
    entries=_build_entries(),
    references=[
      "[1] BS EN 50182. Conductors for overhead lines -- Round wire concentric lay strand conductors, 2001.",
    ],
    standard="BS EN 50182",
  )
