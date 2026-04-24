"""Auditoría integral de nóminas españolas (IRPF + SS) 2012-2026.

Módulo pensado para uso tanto en batch (Excel, gráficos) como en el
navegador vía Pyodide. Por eso `params`, `inflation` y `core` son Python
puro sin dependencias de pandas/numpy.
"""

from irpf.inflation import (
    IPC_ANUAL_DIC,
    inflacion_acumulada,
    multiplicadores_hasta,
)
from irpf.params import obtener_parametros
from irpf.core import calcular_nomina, NominaResultado

__all__ = [
    "IPC_ANUAL_DIC",
    "inflacion_acumulada",
    "multiplicadores_hasta",
    "obtener_parametros",
    "calcular_nomina",
    "NominaResultado",
]
