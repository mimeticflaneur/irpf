"""Generación masiva de tablas (pandas/numpy) a partir del motor ``core``."""

from __future__ import annotations

import numpy as np
import pandas as pd

from irpf.core import calcular_nomina
from irpf.inflation import multiplicadores_hasta
from irpf.params import obtener_parametros


def procesar_ano(anio: int, bruto_max: int = 100_000) -> pd.DataFrame:
    """Tabla exhaustiva (paso 1€) para un ejercicio."""
    p = obtener_parametros(anio)
    filas = []
    for bruto in np.arange(0, bruto_max + 1, 1):
        r = calcular_nomina(float(bruto), anio, p)
        fila = {
            "Salario Bruto": int(bruto),
            "Cot. Soc. Empresa": round(r.cot_empresa, 2),
            "Coste Laboral": round(r.coste_laboral, 2),
            "Cot. Soc. Trab.": round(r.cot_trabajador, 2),
            "Ren. Previo": round(r.rendimiento_previo, 2),
            "Gastos Fijos": r.gastos_fijos,
            "Red. Ren. Trab.": round(r.reduccion_trabajo, 2),
            "Base Imponible": round(r.base_imponible, 2),
        }
        for i, t in enumerate(r.cuotas_tramos, start=1):
            fila[f"T{i} ({round(t['tipo']*100, 1)}%)"] = round(t["cuota"], 2)
        fila.update({
            "Cuota Íntegra": round(r.cuota_integra, 2),
            "Cuota Mínimo Personal": round(r.cuota_minimo_personal, 2),
            "Cuota Teórica": round(r.cuota_teorica, 2),
            "Deducción SMI": round(r.deduccion_smi, 2),
            "Cuota tras SMI": round(r.cuota_tras_smi, 2),
            "Límite 43% (Art 85.3)": round(r.limite_retencion_43, 2),
            "IRPF Final": round(r.irpf_final, 2),
            "Salario Neto": round(r.salario_neto, 2),
        })
        filas.append(fila)
    return pd.DataFrame(filas)


def generar_hojas_control(anio_inicio: int = 2012, anio_fin: int = 2026):
    """Tablas resumen de parámetros normativos y de tramos IRPF."""
    general = []
    tramos = []
    for anio in range(anio_inicio, anio_fin + 1):
        p = obtener_parametros(anio)
        tipo_emp = sum(v[0] for v in p["ss_tipos"].values())
        tipo_tra = sum(v[1] for v in p["ss_tipos"].values())
        general.append({
            "Año": anio,
            "Base Máx. Anual": p["base_max"],
            "SS Empleador %": round(tipo_emp * 100, 2),
            "SS Empleado %": round(tipo_tra * 100, 2),
            "MEI Empleador %": round(p["mei"][0] * 100, 3),
            "MEI Empleado %": round(p["mei"][1] * 100, 3),
            "Gastos Fijos Art.19": p["gastos_fijos"],
            "Mín. Contribuyente": p["irpf_minimo"],
            "Mín. Exento Retención": p["minimo_exento"],
            "Art.20 Umbral Inf": p["art20_meta"]["U_Inf"],
            "Art.20 Red. Máxima": p["art20_meta"]["R_Max"],
            "Art.20 Umbral Sup": p["art20_meta"]["U_Sup"],
            "Art.20 Red. Mínima": p["art20_meta"]["R_Min"],
        })
        for i, (lim, tip) in enumerate(p["tramos_irpf"]):
            tramos.append({
                "Año": anio,
                "Nº Tramo": i + 1,
                "Hasta Base": lim if lim != float("inf") else "En adelante",
                "Tipo %": round(tip * 100, 2),
            })
    return pd.DataFrame(general), pd.DataFrame(tramos)


def generar_comparativa_inflacion(
    anio_ref: int = 2026,
    anio_inicio: int = 2012,
    salarios: range | None = None,
) -> pd.DataFrame:
    """Compara neto real (en euros del año de referencia) por ejercicio."""
    if salarios is None:
        salarios = range(15_000, 100_001, 1000)

    p_ref = obtener_parametros(anio_ref)
    ref = {b: calcular_nomina(float(b), anio_ref, p_ref) for b in salarios}
    mult = multiplicadores_hasta(anio_ref, anio_inicio)

    filas = []
    for anio in range(anio_inicio, anio_ref + 1):
        p = obtener_parametros(anio)
        inf = mult[anio]
        for bruto_ref in salarios:
            bruto_nom = bruto_ref / inf
            r = calcular_nomina(bruto_nom, anio, p)
            c_lab_aj = r.coste_laboral * inf
            c_emp_aj = r.cot_empresa * inf
            c_tra_aj = r.cot_trabajador * inf
            irpf_aj = r.irpf_final * inf
            neto_aj = r.salario_neto * inf
            neto_ref_anio = ref[bruto_ref].salario_neto
            dif = neto_aj - neto_ref_anio
            filas.append({
                "Año a Comparar": anio,
                f"Salario Equivalente ({anio_ref})": bruto_ref,
                "Multiplicador IPC Acum.": round(inf, 4),
                "IPC Acumulado (%)": f"{round((inf - 1) * 100, 2)}%",
                "Salario Bruto Nominal": round(bruto_nom, 2),
                f"Coste Lab. (Euros {anio_ref})": round(c_lab_aj, 2),
                f"SS Emp. (Euros {anio_ref})": round(c_emp_aj, 2),
                f"SS Tra. (Euros {anio_ref})": round(c_tra_aj, 2),
                f"IRPF (Euros {anio_ref})": round(irpf_aj, 2),
                "Neto Real en su Año": round(neto_aj, 2),
                f"Neto Real en {anio_ref}": round(neto_ref_anio, 2),
                f"Variación Poder Adquisitivo Mensual vs {anio_ref} (12 pagas)": round(dif / 12, 2),
                "Pérdida/Ganancia Anual Poder Adq.": round(dif, 2),
            })
    return pd.DataFrame(filas)
