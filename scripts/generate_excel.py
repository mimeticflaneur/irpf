"""Genera el Excel integral de auditoría de nóminas 2012-2026."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from irpf.batch import (
    generar_comparativa_inflacion,
    generar_hojas_control,
    procesar_ano,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path("dist/Auditoria_Integral_Nominas_e_Inflacion_2012_2026.xlsx"))
    parser.add_argument("--anio-inicio", type=int, default=2012)
    parser.add_argument("--anio-fin", type=int, default=2026)
    parser.add_argument("--bruto-max", type=int, default=100_000)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    print(f"Escribiendo {args.output}")
    with pd.ExcelWriter(args.output, engine="openpyxl") as writer:
        print("  → CONTROL_GENERAL / CONTROL_TRAMOS_IRPF")
        df_gen, df_tra = generar_hojas_control(args.anio_inicio, args.anio_fin)
        df_gen.to_excel(writer, sheet_name="CONTROL_GENERAL", index=False)
        df_tra.to_excel(writer, sheet_name="CONTROL_TRAMOS_IRPF", index=False)

        print("  → COMPARATIVA_INFLACION")
        df_comp = generar_comparativa_inflacion(
            anio_ref=args.anio_fin, anio_inicio=args.anio_inicio
        )
        df_comp.to_excel(writer, sheet_name="COMPARATIVA_INFLACION", index=False)

        for anio in range(args.anio_inicio, args.anio_fin + 1):
            print(f"  → DAT_{anio} (paso 1€, hasta {args.bruto_max}€)")
            procesar_ano(anio, args.bruto_max).to_excel(
                writer, sheet_name=f"DAT_{anio}", index=False
            )

    print("Hecho.")


if __name__ == "__main__":
    main()
