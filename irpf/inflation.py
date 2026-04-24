"""IPC anual (diciembre sobre diciembre) e inflación acumulada.

Fuente: INE, índice general nacional, variación interanual en diciembre.
"""

IPC_ANUAL_DIC = {
    2013: 0.003,
    2014: -0.010,
    2015: 0.000,
    2016: 0.016,
    2017: 0.011,
    2018: 0.012,
    2019: 0.008,
    2020: -0.005,
    2021: 0.065,
    2022: 0.057,
    2023: 0.031,
    2024: 0.028,
    2025: 0.029,
    2026: 0.030,
}


def inflacion_acumulada(anio_base: int, anio_destino: int) -> float:
    """Multiplicador para llevar euros de ``anio_base`` a ``anio_destino``."""
    if anio_base == anio_destino:
        return 1.0
    if anio_base > anio_destino:
        return 1.0 / inflacion_acumulada(anio_destino, anio_base)
    multiplicador = 1.0
    for anio in range(anio_base + 1, anio_destino + 1):
        multiplicador *= 1.0 + IPC_ANUAL_DIC[anio]
    return multiplicador


def multiplicadores_hasta(anio_destino: int, anio_inicio: int = 2012) -> dict[int, float]:
    return {a: inflacion_acumulada(a, anio_destino) for a in range(anio_inicio, anio_destino + 1)}
