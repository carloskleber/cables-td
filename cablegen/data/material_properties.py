"""
Dados pré-definidos: Propriedades de materiais condutores.
"""

from cablegen.models import MaterialProperty


MATERIALS = [
  MaterialProperty(
    material="AL 1350", temper="H 19",
    resistivity_ohm_m=2.826e-08, conductivity_s_m=3.538e+07,
    temp_coefficient=4.030e-03, conductivity_iacs_pct=61.0,
    density_g_cm3=2.703, dilatation_coefficient=2.30e-05,
    thermal_conductivity=0.485, reference="[1]",
  ),
  MaterialProperty(
    material="AL 6201", temper="T 81",
    resistivity_ohm_m=3.284e-08, conductivity_s_m=3.045e+07,
    temp_coefficient=3.470e-03, conductivity_iacs_pct=52.5,
    density_g_cm3=2.690, reference="[1]",
  ),
  MaterialProperty(
    material="TAL", temper="H 19",
    resistivity_ohm_m=2.850e-08, conductivity_s_m=3.509e+07,
    temp_coefficient=4.030e-03, conductivity_iacs_pct=60.5,
    density_g_cm3=2.700, reference="[1]",
  ),
  MaterialProperty(
    material="AL 1120", temper="H 16",
    resistivity_ohm_m=2.922e-08, conductivity_s_m=3.422e+07,
    temp_coefficient=3.900e-03, conductivity_iacs_pct=59.0,
    density_g_cm3=2.700, reference="[1]",
  ),
  MaterialProperty(
    material="AL 1120", temper=None,
    resistivity_ohm_m=3.284e-08, conductivity_s_m=3.045e+07,
    temp_coefficient=3.900e-03, conductivity_iacs_pct=52.5,
    density_g_cm3=2.700, modulus_elasticity_gpa=68,
    dilatation_coefficient=2.30e-05, specific_heat_j_g_c=0.9,
    reference="[4]",
  ),
  MaterialProperty(
    material="Steel", temper="ACSR core",
    resistivity_ohm_m=1.916e-07, conductivity_s_m=5.220e+06,
    temp_coefficient=3.200e-03, conductivity_iacs_pct=9.0,
    density_g_cm3=7.780, dilatation_coefficient=1.15e-05,
    thermal_conductivity=0.15, reference="[1]",
  ),
  MaterialProperty(
    material="Copper", temper="HD",
    resistivity_ohm_m=1.777e-08, conductivity_s_m=5.626e+07,
    temp_coefficient=3.810e-03, conductivity_iacs_pct=97.0,
    density_g_cm3=8.890, modulus_elasticity_gpa=124,
    dilatation_coefficient=1.69e-05, specific_heat_j_g_c=0.4,
    reference="[3]",
  ),
  MaterialProperty(
    material="Copper", temper="IACS",
    resistivity_ohm_m=1.724e-08, conductivity_s_m=5.800e+07,
    conductivity_iacs_pct=100.0,
  ),
]

REFERENCES = [
  "[1] ALUBAR. Catálogo Técnico - Condutores Elétricos de Alumínio (Technical Catalogue - Aluminum Electrical Conductors)",
  "[2] MATWEB, LCC. https://matweb.com/",
  "[3] NEXANS. Alúminio - Condutores nus, 2013.",
  "[4] PRYSMIAN. Bare overhead conductors Australia.",
]
