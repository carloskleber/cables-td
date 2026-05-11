# cables-td

Compilation of cable properties for transmission & distribution calculations.

Compilação de propriedades de cabos para estudos de transmissão e distribuição.

The repository is organized as one Markdown file per cable family, plus a separate material properties file. All generated catalog values are intended to be SI units.

## Generator

`cablegen` is the project generator. It produces the catalog Markdown files directly and can also export a pandapower `line` standard-type table.

### Requirements

- Python 3.10+
- Optional online/source refresh and pandapower export: `pip install -r requirements.txt`

### Quick Start

```bash
# Generate catalog Markdown files from built-in data plus valid local source caches
python -m cablegen

# List loaded families and available sources
python -m cablegen --list

# Use only the built-in local families
python -m cablegen --no-sources

# Use one source/cache only
python -m cablegen --source ohl_calcs

# Refresh source data from the network before generating
python -m cablegen --refresh

# Compatibility aliases for refresh
python -m cablegen --fetch
python -m cablegen --force-fetch

# Generate a single family
python -m cablegen --family acsr
python -m cablegen --family aac

# Preview output without writing files
python -m cablegen --dry-run

# Custom output directory
python -m cablegen --output-dir ./output

# Export the pandapower line std_type table
python -m cablegen --std-types
```

By default, `cablegen` uses built-in families and any valid local cache from the configured sources. It only accesses the network with `--refresh` or the compatibility aliases `--fetch` / `--force-fetch`.

Normal catalog Markdown generation does not require pandapower. Pandapower is required only for `--std-types`.

### Built-in Data

| Family | Entries | Standard |
|--------|---------|----------|
| ACSR | 82 | ASTM B232 / ABNT NBR 7270 |
| ACSR (EN) | 36 | BS EN 50182 |
| ACAR (Midal metric) | 229 | Midal Metric |
| Material Properties | 8 | Various |

### Sources

| Source | Families | Type |
|--------|----------|------|
| [ohl-calcs](https://github.com/LiaungYip/ohl-calcs) | AAC, AAAC, ACSR, AACSR, Copper, Steel Core | CSV download/cache |
| [ChampWire](https://champwire.com/product-type/transmission-distribution-cable/) | AAC, AAAC, ACAR, ACSR, ACSR-AW, ACSR-TW, ACSS, ACSS-AW, ACSS-TW, Copper | HTML scraping/cache |
| [Priority Wire](https://www.prioritywire.com/) | AAC, AAAC, ACAR, ACSR | HTML scraping/cache |

### Pandapower Export

`python -m cablegen --std-types` converts the loaded cable catalog into pandapower `line` standard types and writes `pandapower_line_types.md`.

The physical cable catalogs provide DC resistance and mechanical/geometric data, but not all pandapower line parameters. The pandapower export therefore uses configurable assumptions:

```bash
python -m cablegen --std-types --x-ohm-per-km 0.4 --c-nf-per-km 10 --max-i-ka 1.0
```

These assumptions affect only the pandapower `std_type` export, not the physical catalog Markdown files.

## Português

Este repositório compila propriedades de cabos para estudos de transmissão e distribuição. Ele é organizado em um arquivo Markdown por família de cabos, além de um arquivo separado para propriedades de materiais. As unidades geradas no catálogo devem estar em SI.

## Gerador

`cablegen` é o gerador do projeto. Ele gera diretamente os arquivos Markdown de catálogo e também pode exportar uma tabela de tipos padrão de linha do pandapower.

### Requisitos

- Python 3.10+
- Para atualizar fontes online e/ou exportar pandapower: `pip install -r requirements.txt`

### Uso Rápido

```bash
# Gerar Markdown de catálogo com dados embutidos e caches locais válidos
python -m cablegen

# Listar famílias carregadas e fontes disponíveis
python -m cablegen --list

# Usar apenas famílias locais embutidas
python -m cablegen --no-sources

# Usar apenas um cache/fonte
python -m cablegen --source ohl_calcs

# Atualizar dados das fontes pela rede antes de gerar
python -m cablegen --refresh

# Aliases de compatibilidade para refresh
python -m cablegen --fetch
python -m cablegen --force-fetch

# Gerar apenas uma família
python -m cablegen --family acsr
python -m cablegen --family aac

# Previsualizar sem salvar
python -m cablegen --dry-run

# Diretório de saída customizado
python -m cablegen --output-dir ./output

# Exportar a tabela pandapower line std_type
python -m cablegen --std-types
```

Por padrão, o `cablegen` usa famílias embutidas e qualquer cache local válido das fontes configuradas. Ele só acessa a rede com `--refresh` ou com os aliases de compatibilidade `--fetch` / `--force-fetch`.

A geração normal dos Markdown de catálogo não exige pandapower. O pandapower é necessário apenas para `--std-types`.

### Exportação Pandapower

`python -m cablegen --std-types` converte o catálogo carregado para tipos padrão de linha do pandapower e escreve `pandapower_line_types.md`.

Os catálogos físicos fornecem resistência DC e dados mecânicos/geométricos, mas não todos os parâmetros de linha exigidos pelo pandapower. Por isso, a exportação pandapower usa premissas configuráveis:

```bash
python -m cablegen --std-types --x-ohm-per-km 0.4 --c-nf-per-km 10 --max-i-ka 1.0
```

Essas premissas afetam apenas a exportação `std_type` do pandapower, não os arquivos Markdown do catálogo físico.
