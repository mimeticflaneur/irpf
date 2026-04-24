# Calculadora

Ejecuta el **mismo motor Python** que genera el Excel, pero dentro de tu
navegador (vía [Pyodide](https://pyodide.org)). Es decir: los números que
ves aquí son bit-a-bit los que salen del repositorio — nada se reescribe
en JavaScript.

> La primera carga descarga ~6 MB de runtime Python. Una vez cargado,
> cada cálculo es instantáneo.

<div id="calc-app" markdown="0">
  <form id="calc-form" class="calc-form">
    <label>
      Salario bruto anual (€)
      <input type="number" id="calc-bruto" value="30000" min="0" step="100">
    </label>
    <label>
      Ejercicio
      <select id="calc-anio">
        <option value="2012">2012</option>
        <option value="2013">2013</option>
        <option value="2014">2014</option>
        <option value="2015">2015</option>
        <option value="2016">2016</option>
        <option value="2017">2017</option>
        <option value="2018">2018</option>
        <option value="2019">2019</option>
        <option value="2020">2020</option>
        <option value="2021">2021</option>
        <option value="2022">2022</option>
        <option value="2023">2023</option>
        <option value="2024">2024</option>
        <option value="2025">2025</option>
        <option value="2026" selected>2026</option>
      </select>
    </label>
    <button type="submit" id="calc-submit" disabled>Cargando Pyodide…</button>
  </form>
  <div id="calc-status" class="calc-status">Inicializando Python en el navegador…</div>
  <div id="calc-result" class="calc-result"></div>
</div>
