"""Smoke tests: se comprueban invariantes y valores ancla del motor."""

from __future__ import annotations

import math

from irpf.core import calcular_nomina
from irpf.inflation import inflacion_acumulada
from irpf.params import obtener_parametros


def test_bruto_cero_en_todo_el_periodo():
    for anio in range(2012, 2027):
        p = obtener_parametros(anio)
        r = calcular_nomina(0.0, anio, p)
        assert r.cot_trabajador == 0
        assert r.cot_empresa == 0
        assert r.irpf_final == 0
        assert r.salario_neto == 0


def test_identidad_contable():
    """bruto = neto + IRPF + SS trabajador"""
    for anio in range(2012, 2027):
        p = obtener_parametros(anio)
        for bruto in (8_000, 18_000, 30_000, 60_000, 120_000):
            r = calcular_nomina(float(bruto), anio, p)
            suma = r.salario_neto + r.irpf_final + r.cot_trabajador
            assert math.isclose(suma, bruto, abs_tol=0.01), (
                f"{anio} bruto {bruto}: {suma} != {bruto}"
            )


def test_coste_laboral_incluye_css_empresa():
    p = obtener_parametros(2025)
    r = calcular_nomina(40_000.0, 2025, p)
    assert math.isclose(r.coste_laboral, r.bruto + r.cot_empresa, abs_tol=0.01)


def test_solidaridad_solo_2025_en_adelante():
    for anio in (2012, 2020, 2023, 2024):
        p = obtener_parametros(anio)
        assert p["solidaridad"] == []
    for anio in (2025, 2026):
        p = obtener_parametros(anio)
        assert len(p["solidaridad"]) == 3


def test_inflacion_acumulada_identidad():
    assert inflacion_acumulada(2020, 2020) == 1.0
    ida = inflacion_acumulada(2015, 2024)
    vuelta = inflacion_acumulada(2024, 2015)
    assert math.isclose(ida * vuelta, 1.0, abs_tol=1e-9)


def test_limite_43_porcentaje_aplica_a_brutos_bajos():
    """Para brutos poco superiores al mínimo exento, el IRPF está capado al 43%."""
    p = obtener_parametros(2026)
    r = calcular_nomina(16_000.0, 2026, p)
    assert r.irpf_final <= r.limite_retencion_43 + 1e-6
