"""
Command-line interface for the pandapower-based generator.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cablegen.adapter import (
  LineTypeAssumptions,
  available_line_types,
  catalog_line_types,
  create_catalog_network,
  get_sources,
  load_families,
  register_line_types,
)
from cablegen.catalog_renderer import render_catalog_files
from cablegen.renderer import render_line_types_markdown, write_output


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    prog="cablegen",
    description="Gerador de listas de cabos baseado em pandapower std_types.",
  )
  parser.add_argument("--family", help="Gerar apenas uma família (ex: acsr, acar).")
  parser.add_argument("--list", action="store_true", help="Listar famílias e fontes.")
  parser.add_argument(
    "--no-sources",
    action="store_true",
    help="Usar apenas famílias embutidas, ignorando caches/fontes.",
  )
  parser.add_argument(
    "--refresh",
    action="store_true",
    help="Atualizar dados das fontes online antes de gerar.",
  )
  parser.add_argument(
    "--fetch",
    action="store_true",
    help="Alias de compatibilidade para --refresh.",
  )
  parser.add_argument("--source", help="Usar uma fonte específica (ex: ohl_calcs).")
  parser.add_argument("--force-fetch", action="store_true", help="Alias de compatibilidade para --refresh.")
  parser.add_argument("--dry-run", action="store_true", help="Mostrar output sem salvar.")
  parser.add_argument(
    "--output-dir",
    default=None,
    help="Diretório de saída (padrão: raiz do projeto).",
  )
  parser.add_argument(
    "--output",
    default="pandapower_line_types.md",
    help="Nome do arquivo Markdown para --std-types.",
  )
  parser.add_argument(
    "--std-types",
    action="store_true",
    help="Gerar relatório único com a tabela pandapower available_std_types.",
  )
  parser.add_argument(
    "--no-materials",
    action="store_true",
    help="Não gerar material_properties.md no modo catálogo.",
  )
  parser.add_argument(
    "--x-ohm-per-km",
    type=float,
    default=LineTypeAssumptions.x_ohm_per_km,
    help="Reatância série assumida para std_types de linha.",
  )
  parser.add_argument(
    "--c-nf-per-km",
    type=float,
    default=LineTypeAssumptions.c_nf_per_km,
    help="Capacitância assumida para std_types de linha.",
  )
  parser.add_argument(
    "--max-i-ka",
    type=float,
    default=LineTypeAssumptions.default_max_i_ka,
    help="Corrente máxima assumida quando a entrada não possui ampacidade.",
  )
  return parser


def main(argv: list[str] | None = None) -> None:
  args = build_parser().parse_args(argv)
  try:
    families = load_families(
      args.family,
      include_sources=not args.no_sources,
      source_name=args.source,
      refresh=args.refresh or args.fetch or args.force_fetch,
    )
  except ValueError as exc:
    print(f"Erro: {exc}", file=sys.stderr)
    sys.exit(1)

  if args.list:
    print("Famílias:")
    for family in families:
      print(f"{family.name}: {len(family.entries)} entradas -> {family.output_filename}")
    print("\nFontes:")
    for name, source in get_sources().items():
      print(f"{name}: {', '.join(source.available_families())}")
    return

  assumptions = LineTypeAssumptions(
    x_ohm_per_km=args.x_ohm_per_km,
    c_nf_per_km=args.c_nf_per_km,
    default_max_i_ka=args.max_i_ka,
  )
  output_dir = Path(args.output_dir) if args.output_dir else _project_root()
  if args.std_types:
    try:
      net = create_catalog_network(families, assumptions)
      table = catalog_line_types(net)
    except RuntimeError as exc:
      print(f"Erro: {exc}", file=sys.stderr)
      sys.exit(1)
    content = render_line_types_markdown(table, families, assumptions)
    write_output(content, output_dir / args.output, dry_run=args.dry_run)
    print(f"OK: {len(table)} pandapower line std_types disponíveis.")
    return

  render_catalog_files(
    families,
    output_dir,
    dry_run=args.dry_run,
    no_materials=args.no_materials,
  )
  print(f"OK: {len(families)} arquivos de famílias gerados.")


def _project_root() -> Path:
  return Path(__file__).resolve().parent.parent


__all__ = [
  "LineTypeAssumptions",
  "available_line_types",
  "catalog_line_types",
  "create_catalog_network",
  "get_sources",
  "load_families",
  "register_line_types",
]
