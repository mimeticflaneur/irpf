# Auditoría integral de nóminas en España (2012-2026)

[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://mimeticflaneur.github.io/irpf/)
[![Code license: MIT](https://img.shields.io/badge/code-MIT-green.svg)](./LICENSE)
[![Data license: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey.svg)](./LICENSE-DATA)

Datos abiertos y metodología auditable del cálculo de nóminas en España:
**IRPF**, **Seguridad Social**, **MEI**, **cuota de solidaridad** y **ajuste
por inflación** (IPC dic-dic, INE) para cada ejercicio entre 2012 y 2026.

> **Web**: <https://mimeticflaneur.github.io/irpf/> — metodología, tablas,
> gráficos interactivos y una **calculadora que corre el mismo motor Python
> del repo en tu navegador** (vía Pyodide). Cero backend.

## Qué hay en este repo

```
irpf/
  inflation.py   IPC dic-dic y multiplicadores acumulados (Python puro)
  params.py      Parámetros normativos por ejercicio (Python puro)
  core.py        Motor de cálculo de nómina (Python puro, Pyodide-friendly)
  batch.py       Generación masiva vía pandas/numpy
scripts/
  generate_excel.py    Genera el Excel integral 2012-2026
  generate_charts.py   Genera los gráficos Plotly para la web
docs/              Web (MkDocs Material) y hooks Pyodide
tests/             Smoke tests del motor
```

El motor (`params`, `inflation`, `core`) no depende de `pandas` ni `numpy`:
es el **mismo código** que ejecuta Pyodide en la web y `batch.py` en batch.
Una sola fuente de verdad.

## Uso rápido

```bash
pip install -r requirements.txt

# Excel con 15 hojas anuales (paso 1€) + comparativa inflación + control
python scripts/generate_excel.py --output dist/auditoria.xlsx

# Gráficos Plotly (se incrustan en la web)
python scripts/generate_charts.py

# Web local
pip install -r docs-requirements.txt
mkdocs serve
```

## Metodología (resumen)

1. Base de cotización = `min(bruto, base_max_anual)`.
2. SS trabajador y SS empresa con tipos por contingencia + MEI (2023+).
3. Cuota de solidaridad sobre el exceso de base (2025+), reparto 5/6–1/6.
4. Rendimiento neto = bruto − SS trabajador − gastos fijos art. 19.
5. Reducción por rendimientos del trabajo (art. 20), con régimen transitorio
   en 2018.
6. Cuota íntegra por tramos (escala estatal supletoria).
7. Cuota del mínimo personal aplicada al tipo del primer tramo.
8. Deducción SMI (2025-2026, art. 85.3 RIRPF).
9. Límite del 43% sobre (bruto − mínimo exento).

Detalle completo con fórmulas y fuentes en
[`docs/metodologia.md`](./docs/metodologia.md) y
[`docs/fuentes.md`](./docs/fuentes.md).

## Limitaciones

- Residencia fiscal en territorio común (no foral).
- Sin particularidades personales (hijos, ascendientes, minusvalía,
  maternidad, pensión compensatoria).
- Escala autonómica = estatal supletoria (cada CC.AA. tiene la suya).
- Rendimientos del trabajo regulares exclusivamente (sin irregulares ni
  retribuciones en especie).

## Contribuir

Si detectas una discrepancia con el BOE o con la nómina real:

1. Abre un issue citando la referencia oficial.
2. (Opcional) Envía un PR tocando el parámetro en `irpf/params.py` o
   `irpf/inflation.py` con la fuente en el mensaje del commit.

## Licencias

- **Código**: [MIT](./LICENSE).
- **Datos y documentación** (contenido de `docs/` y Excel generado):
  [CC BY 4.0](./LICENSE-DATA).
