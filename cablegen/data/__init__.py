"""
Pacote com dados pré-definidos de cabos condutores.

Cada módulo exporta uma função `get_family()` que retorna
um `CableFamily` com os dados da respectiva família.
"""

from cablegen.models import CableFamily

def get_all_families() -> list[CableFamily]:
  """Retorna todas as famílias predefinidas."""
  from cablegen.data.acsr_astm import get_family as get_acsr_astm
  from cablegen.data.acsr_en import get_family as get_acsr_en
  from cablegen.data.acar_midal import get_family as get_acar_midal

  return [
    get_acsr_astm(),
    get_acsr_en(),
    get_acar_midal(),
  ]
