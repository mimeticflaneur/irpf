# Auditoría integral de nóminas en España (2012-2026)

Proyecto **open source** que reconstruye la nómina española — IRPF, cotizaciones
a la Seguridad Social, MEI, cuota de solidaridad y ajuste por inflación — para
cada ejercicio entre 2012 y 2026, con **datos y metodología totalmente
auditables**.

## Qué encontrarás aquí

- **[Metodología](metodologia.md)** — cómo se calcula cada partida, paso a paso,
  con las fórmulas oficiales.
- **[Datos y parámetros](datos.md)** — tablas normativas por ejercicio
  (bases máximas, tramos IRPF, reducciones del art. 20, MEI, solidaridad...).
- **[Gráficos interactivos](graficos.md)** — evolución del salario neto, tipo
  efectivo total y pérdida de poder adquisitivo frente a hoy.
- **[Calculadora](calculadora.md)** — corre el mismo motor Python en tu navegador
  (vía Pyodide) para cualquier salario bruto y ejercicio.
- **[Fuentes oficiales](fuentes.md)** — referencias al BOE, AEAT e INE para
  cada parámetro.

## Reproducibilidad

Todo el cálculo es determinista y está en [el repositorio](https://github.com/mimeticflaneur/irpf):

```bash
pip install -r requirements.txt
python -m scripts.generate_excel        # Excel con 15 hojas anuales + control
python -m scripts.generate_charts       # Gráficos Plotly
mkdocs serve                            # Web local en http://127.0.0.1:8000
```

## Licencia

- **Código**: [MIT](https://github.com/mimeticflaneur/irpf/blob/main/LICENSE)
- **Datos y documentación**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es)

## Aviso

Este proyecto tiene fines **informativos y divulgativos**. No sustituye al
asesoramiento fiscal profesional ni a las calculadoras oficiales de la AEAT.
Siempre que detectes una discrepancia con la nómina real o con el simulador
oficial, abre un issue: la prioridad es que los datos cuadren con el BOE.
