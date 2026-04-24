# Metodología

Todo el cálculo está implementado en [`irpf/core.py`](https://github.com/mimeticflaneur/irpf/blob/main/irpf/core.py).
Esta página describe, en el mismo orden en que lo ejecuta el motor, cómo se
construye la nómina anual para un salario bruto dado.

Asumimos contrato **indefinido a tiempo completo, régimen general**, sin
particularidades (hijos, minusvalías, pensión, reducciones autonómicas...).

## 1. Base de cotización

$$
B_\text{cot} = \min(\text{bruto},\ B_\text{máx})
\qquad
\text{Exceso} = \max(0,\ \text{bruto} - B_\text{máx})
$$

La base máxima anual la fija la LPGE y se actualiza por RD-ley. Los valores se
listan en [Datos y parámetros](datos.md).

## 2. Cotizaciones a la Seguridad Social

Tipo total de cada parte:

$$
t_\text{emp} = \sum_k \tau^\text{emp}_k + \text{MEI}^\text{emp}
\qquad
t_\text{tra} = \sum_k \tau^\text{tra}_k + \text{MEI}^\text{tra}
$$

con $k \in \{\text{comunes, desempleo, FOGASA, FP, ATEP}\}$ y el **MEI**
(Mecanismo de Equidad Intergeneracional) vigente desde 2023.

$$
\text{CSS}_\text{emp} = B_\text{cot} \cdot t_\text{emp}
\qquad
\text{CSS}_\text{tra} = B_\text{cot} \cdot t_\text{tra}
$$

### 2.1 Cuota de solidaridad (2025+)

Para salarios por encima de la base máxima se añade una cuota sobre el exceso:

| Tramo sobre el exceso                 | 2025    | 2026    |
|---------------------------------------|---------|---------|
| Hasta 10% de la base máx.             | 0,92%   | 1,15%   |
| Del 10% al 50%                        | 1,00%   | 1,25%   |
| Más del 50%                           | 1,17%   | 1,46%   |

El reparto es el mismo que el resto de contingencias comunes: **5/6 empresa,
1/6 trabajador** (art. 19 bis LGSS).

## 3. Rendimiento neto del trabajo (IRPF)

$$
R_\text{previo} = \text{bruto} - \text{CSS}_\text{tra}
$$

$$
R_\text{neto} = \max(0,\ R_\text{previo} - G_\text{fijos})
$$

Los **gastos deducibles fijos** del art. 19 LIRPF son 2.000 € desde 2015 (0 €
antes).

### 3.1 Reducción por rendimientos del trabajo (art. 20)

Es la pieza que más veces ha cambiado. Por ejercicio (ver detalle en
[`irpf/params.py`](https://github.com/mimeticflaneur/irpf/blob/main/irpf/params.py)):

- **2012-2014**: máx. 4.080 €, mín. 2.652 €.
- **2015-2017**: máx. 3.700 €, mín. 0 € (reforma Ley 26/2014).
- **2018**: régimen transitorio (media aritmética entre las dos tablas).
- **2019-2022**: máx. 5.565 € (RD-ley 27/2018 y siguientes).
- **2023**: máx. 6.498 € (Ley 31/2022).
- **2024+**: máx. 7.302 € con tramo adicional en 14.852 € → 17.673,52 €
  (Ley 31/2022 y RD-ley 8/2023).

$$
BI = \max(0,\ R_\text{neto} - \text{red}_\text{art.20})
$$

## 4. Cuota íntegra

Aplicación por tramos de la escala conjunta (estatal + autonómica media):

$$
C_\text{íntegra} = \sum_i (BI_i - BI_{i-1}) \cdot t_i
$$

## 5. Mínimo personal y familiar

Se aplica sobre la escala al tipo del primer tramo (art. 56 LIRPF):

$$
C_\text{mínimo} = M_\text{personal} \cdot t_1
$$

$$
C_\text{teórica} = \max(0,\ C_\text{íntegra} - C_\text{mínimo})
$$

## 6. Deducción por SMI (art. 85.3 RIRPF, 2025-2026)

En 2025 y 2026 existe una reducción específica sobre la retención calculada
para trabajadores que cobran en el entorno del SMI. Ver [`params.py`](https://github.com/mimeticflaneur/irpf/blob/main/irpf/params.py)
para los umbrales exactos.

## 7. Límite del 43% (art. 85.3 RIRPF)

La retención resultante nunca puede exceder el 43% de la diferencia entre
el bruto y el mínimo exento de retención:

$$
\text{IRPF}_\text{final} = \min\!\bigl(C_\text{tras SMI},\ 0{,}43 \cdot \max(0,\text{bruto} - M_\text{exento})\bigr)
$$

## 8. Salario neto

$$
\text{Neto} = \text{bruto} - \text{CSS}_\text{tra} - \text{IRPF}_\text{final}
$$

## 9. Ajuste por inflación

Para comparar ejercicios usamos el **IPC anual diciembre-diciembre** (INE,
índice general nacional). El multiplicador para llevar € de $a$ a $b$ es:

$$
M_{a \to b} = \prod_{k=a+1}^{b} (1 + \pi_k)
$$

con $\pi_k$ = variación interanual en diciembre del año $k$. La serie exacta
está en [`irpf/inflation.py`](https://github.com/mimeticflaneur/irpf/blob/main/irpf/inflation.py).

## Limitaciones conocidas

- Se asume **residente fiscal en territorio común** (no forales), **sin
  particularidades personales** (descendientes, ascendientes, minusvalía).
- La escala autonómica usada es la **estatal supletoria**; en la práctica
  cada CC.AA. aplica su propia tabla (diferencias habituales ±1-3%).
- El régimen de **reducción por rendimientos irregulares** y los complementos
  en especie quedan fuera.
- Los cálculos son **anuales**; la nómina mensual se obtiene dividiendo por
  12 o 14 según se indique.
