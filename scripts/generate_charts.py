"""Genera los gráficos interactivos (Plotly HTML) que consume la web."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

from irpf.core import calcular_nomina
from irpf.inflation import IPC_ANUAL_DIC, multiplicadores_hasta
from irpf.params import obtener_parametros


PLOTLY_CONFIG = {"displaylogo": False, "responsive": True}


def _salarios(paso: int = 250, tope: int = 100_000):
    return np.arange(0, tope + 1, paso)


def fig_neto_por_anio(anios: range, out: Path) -> None:
    salarios = _salarios(250)
    fig = go.Figure()
    for anio in anios:
        p = obtener_parametros(anio)
        netos = [calcular_nomina(float(b), anio, p).salario_neto for b in salarios]
        fig.add_trace(go.Scatter(x=salarios, y=netos, mode="lines", name=str(anio)))
    fig.update_layout(
        title="Salario neto nominal por ejercicio",
        xaxis_title="Salario bruto anual (€)",
        yaxis_title="Salario neto anual (€)",
        hovermode="x unified",
    )
    fig.write_html(out, include_plotlyjs="cdn", config=PLOTLY_CONFIG, full_html=False)


def fig_tipo_efectivo(anios: range, out: Path) -> None:
    salarios = _salarios(250)
    fig = go.Figure()
    for anio in anios:
        p = obtener_parametros(anio)
        tipos = []
        for b in salarios:
            if b == 0:
                tipos.append(0.0)
                continue
            r = calcular_nomina(float(b), anio, p)
            tipos.append((r.irpf_final + r.cot_trabajador) / b * 100.0)
        fig.add_trace(go.Scatter(x=salarios, y=tipos, mode="lines", name=str(anio)))
    fig.update_layout(
        title="Tipo efectivo total (IRPF + SS trabajador) sobre bruto",
        xaxis_title="Salario bruto anual (€)",
        yaxis_title="Tipo efectivo (%)",
        hovermode="x unified",
    )
    fig.write_html(out, include_plotlyjs="cdn", config=PLOTLY_CONFIG, full_html=False)


def fig_ipc_acumulado(anio_ref: int, anio_inicio: int, out: Path) -> None:
    mult = multiplicadores_hasta(anio_ref, anio_inicio)
    anios = sorted(mult.keys())
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=anios,
        y=[round((mult[a] - 1) * 100, 2) for a in anios],
        name="IPC acumulado hasta " + str(anio_ref),
    ))
    fig.update_layout(
        title=f"IPC acumulado desde cada año hasta {anio_ref} (%)",
        xaxis_title="Año base",
        yaxis_title=f"% de inflación acumulada a {anio_ref}",
    )
    fig.write_html(out, include_plotlyjs="cdn", config=PLOTLY_CONFIG, full_html=False)


def fig_perdida_poder_adquisitivo(anio_ref: int, anio_inicio: int, bruto_ref: int, out: Path) -> None:
    mult = multiplicadores_hasta(anio_ref, anio_inicio)
    p_ref = obtener_parametros(anio_ref)
    neto_ref = calcular_nomina(float(bruto_ref), anio_ref, p_ref).salario_neto

    anios, difs = [], []
    for anio in sorted(mult.keys()):
        p = obtener_parametros(anio)
        inf = mult[anio]
        r = calcular_nomina(bruto_ref / inf, anio, p)
        neto_aj = r.salario_neto * inf
        anios.append(anio)
        difs.append(round(neto_aj - neto_ref, 2))

    fig = go.Figure()
    fig.add_trace(go.Bar(x=anios, y=difs, name=f"Bruto {bruto_ref}€ ({anio_ref})"))
    fig.update_layout(
        title=(f"Pérdida/ganancia anual de poder adquisitivo frente a {anio_ref}"
               f" (bruto equivalente {bruto_ref}€)"),
        xaxis_title="Año comparado",
        yaxis_title=f"€ {anio_ref} anuales vs {anio_ref}",
    )
    fig.write_html(out, include_plotlyjs="cdn", config=PLOTLY_CONFIG, full_html=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("docs/assets/charts"))
    parser.add_argument("--anio-inicio", type=int, default=2012)
    parser.add_argument("--anio-fin", type=int, default=max(IPC_ANUAL_DIC))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    anios = range(args.anio_inicio, args.anio_fin + 1)

    print("Generando gráficos Plotly...")
    fig_neto_por_anio(anios, args.output_dir / "neto_por_anio.html")
    fig_tipo_efectivo(anios, args.output_dir / "tipo_efectivo.html")
    fig_ipc_acumulado(args.anio_fin, args.anio_inicio, args.output_dir / "ipc_acumulado.html")
    for bruto in (20_000, 30_000, 45_000, 70_000):
        fig_perdida_poder_adquisitivo(
            args.anio_fin, args.anio_inicio, bruto,
            args.output_dir / f"poder_adquisitivo_{bruto}.html",
        )
    print(f"Gráficos en {args.output_dir}/")


if __name__ == "__main__":
    main()
