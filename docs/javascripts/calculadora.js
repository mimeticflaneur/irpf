// Carga Pyodide, descarga los módulos del paquete `irpf` desde /assets/pyodide/
// y expone una UI que llama al mismo `calcular_nomina` del repo.

const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js";
const MODULES = ["inflation.py", "params.py", "core.py"];

function fmt(n) {
  if (n === null || n === undefined) return "—";
  return n.toLocaleString("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

async function loadPyodideOnce() {
  if (window.__pyodide) return window.__pyodide;
  await new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = PYODIDE_URL;
    s.onload = resolve;
    s.onerror = reject;
    document.head.appendChild(s);
  });
  const pyodide = await loadPyodide();
  const base = (document.querySelector("base")?.href || "").replace(/\/$/, "");
  const assetsBase = `${base || ""}/assets/pyodide`;
  for (const mod of MODULES) {
    const res = await fetch(`${assetsBase}/${mod}`);
    if (!res.ok) throw new Error(`No se pudo cargar ${mod}`);
    const code = await res.text();
    pyodide.FS.writeFile(`/home/pyodide/${mod}`, code);
  }
  pyodide.runPython(`
import sys
sys.path.insert(0, "/home/pyodide")
import params
import core
from dataclasses import asdict
`);
  window.__pyodide = pyodide;
  return pyodide;
}

function render(result) {
  const rows = [
    ["Salario bruto", result.bruto, false],
    ["Base de cotización", result.base_cotizacion, false],
    ["Exceso sobre base máx.", result.exceso_base, false],
    ["Cot. SS trabajador", -result.cot_trabajador, false],
    ["Cot. SS empresa (informativo)", result.cot_empresa, false],
    ["Coste laboral total (informativo)", result.coste_laboral, false],
    ["Rendimiento previo", result.rendimiento_previo, false],
    ["Gastos fijos (art. 19)", -result.gastos_fijos, false],
    ["Reducción art. 20", -result.reduccion_trabajo, false],
    ["Base imponible", result.base_imponible, false],
    ["Cuota íntegra", result.cuota_integra, false],
    ["Cuota mínimo personal", -result.cuota_minimo_personal, false],
    ["Cuota teórica", result.cuota_teorica, false],
    ["Deducción SMI", -result.deduccion_smi, false],
    ["Límite 43% (art. 85.3)", result.limite_retencion_43, false],
    ["IRPF final", -result.irpf_final, false],
    ["Salario neto", result.salario_neto, true],
  ];
  const body = rows.map(([label, value, hl]) => `
    <tr class="${hl ? "highlight" : ""}">
      <td>${label}</td>
      <td class="num">${fmt(value)} €</td>
    </tr>
  `).join("");
  return `<table><tbody>${body}</tbody></table>`;
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("calc-form");
  if (!form) return;
  const btn = document.getElementById("calc-submit");
  const status = document.getElementById("calc-status");
  const result = document.getElementById("calc-result");

  loadPyodideOnce()
    .then(() => {
      btn.disabled = false;
      btn.textContent = "Calcular";
      status.textContent = "Listo.";
    })
    .catch((err) => {
      status.textContent = `Error cargando Pyodide: ${err.message}`;
    });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const bruto = parseFloat(document.getElementById("calc-bruto").value);
    const anio = parseInt(document.getElementById("calc-anio").value, 10);
    if (isNaN(bruto) || bruto < 0) {
      status.textContent = "Introduce un bruto válido.";
      return;
    }
    status.textContent = "Calculando…";
    const pyodide = await loadPyodideOnce();
    pyodide.globals.set("js_bruto", bruto);
    pyodide.globals.set("js_anio", anio);
    pyodide.runPython(`
p = params.obtener_parametros(int(js_anio))
_res = core.calcular_nomina(float(js_bruto), int(js_anio), p)
_dict = asdict(_res)
`);
    const data = pyodide.globals.get("_dict").toJs({ dict_converter: Object.fromEntries });
    result.innerHTML = render(data);
    status.textContent = `Cálculo para ${anio} completado.`;
  });
});
