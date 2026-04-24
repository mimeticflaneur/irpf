"""Motor de cálculo de nómina (Python puro, sin numpy/pandas).

Este módulo es el mismo que corre el navegador vía Pyodide: no depende de
ninguna librería externa para que el cálculo sea idéntico en batch y en web.
"""

from dataclasses import dataclass, field


@dataclass
class NominaResultado:
    anio: int
    bruto: float
    base_cotizacion: float
    exceso_base: float
    cot_empresa: float
    cot_trabajador: float
    coste_laboral: float
    rendimiento_previo: float
    gastos_fijos: float
    reduccion_trabajo: float
    base_imponible: float
    cuotas_tramos: list = field(default_factory=list)
    cuota_integra: float = 0.0
    cuota_minimo_personal: float = 0.0
    cuota_teorica: float = 0.0
    deduccion_smi: float = 0.0
    cuota_tras_smi: float = 0.0
    limite_retencion_43: float = 0.0
    irpf_final: float = 0.0
    salario_neto: float = 0.0


def _cuotas_por_tramo(base_liq: float, tramos):
    cuotas = []
    total = 0.0
    if base_liq <= 0:
        for _, tipo in tramos:
            cuotas.append({"tipo": tipo, "cuota": 0.0})
        return cuotas, total
    lim_ant = 0.0
    agotado = False
    for lim, tipo in tramos:
        if agotado:
            cuotas.append({"tipo": tipo, "cuota": 0.0})
            continue
        if base_liq > lim:
            cuota = (lim - lim_ant) * tipo
            cuotas.append({"tipo": tipo, "cuota": cuota})
            total += cuota
            lim_ant = lim
        else:
            cuota = (base_liq - lim_ant) * tipo
            cuotas.append({"tipo": tipo, "cuota": cuota})
            total += cuota
            agotado = True
    return cuotas, total


def calcular_nomina(bruto: float, anio: int, p: dict) -> NominaResultado:
    """Calcula el desglose completo de una nómina para un bruto y año dados."""
    base_cotizacion = min(bruto, p["base_max"])
    exceso_base = max(0.0, bruto - p["base_max"])

    tipo_empresa = sum(v[0] for v in p["ss_tipos"].values()) + p["mei"][0]
    tipo_trabajador = sum(v[1] for v in p["ss_tipos"].values()) + p["mei"][1]

    cot_empresa = base_cotizacion * tipo_empresa
    cot_trabajador = base_cotizacion * tipo_trabajador

    if p["solidaridad"] and exceso_base > 0:
        tramo1 = p["base_max"] * 0.10
        tramo2 = p["base_max"] * 0.50
        e1 = min(exceso_base, tramo1)
        e2 = min(max(0.0, exceso_base - tramo1), tramo2 - tramo1)
        e3 = max(0.0, exceso_base - tramo2)
        cuota_sol = (e1 * p["solidaridad"][0][1]
                     + e2 * p["solidaridad"][1][1]
                     + e3 * p["solidaridad"][2][1])
        cot_empresa += cuota_sol * (5.0 / 6.0)
        cot_trabajador += cuota_sol * (1.0 / 6.0)

    coste_laboral = bruto + cot_empresa

    rendimiento_previo = bruto - cot_trabajador
    red_trabajo = p["reduccion_trabajo"](rendimiento_previo)
    rendimiento_neto = max(0.0, rendimiento_previo - p["gastos_fijos"])
    base_imponible = max(0.0, rendimiento_neto - red_trabajo)

    cuotas_tramos, cuota_integra = _cuotas_por_tramo(base_imponible, p["tramos_irpf"])
    cuota_minimo = p["irpf_minimo"] * p["tramos_irpf"][0][1]
    cuota_teorica = max(0.0, cuota_integra - cuota_minimo)

    deduccion = p["deduccion_smi"](bruto)
    cuota_tras_smi = max(0.0, cuota_teorica - deduccion)

    limite_ret = max(0.0, (bruto - p["minimo_exento"]) * 0.43)
    irpf_final = min(cuota_tras_smi, limite_ret)
    salario_neto = bruto - cot_trabajador - irpf_final

    return NominaResultado(
        anio=anio,
        bruto=bruto,
        base_cotizacion=base_cotizacion,
        exceso_base=exceso_base,
        cot_empresa=cot_empresa,
        cot_trabajador=cot_trabajador,
        coste_laboral=coste_laboral,
        rendimiento_previo=rendimiento_previo,
        gastos_fijos=p["gastos_fijos"],
        reduccion_trabajo=red_trabajo,
        base_imponible=base_imponible,
        cuotas_tramos=cuotas_tramos,
        cuota_integra=cuota_integra,
        cuota_minimo_personal=cuota_minimo,
        cuota_teorica=cuota_teorica,
        deduccion_smi=deduccion,
        cuota_tras_smi=cuota_tras_smi,
        limite_retencion_43=limite_ret,
        irpf_final=irpf_final,
        salario_neto=salario_neto,
    )
