"""Hook de MkDocs: copia los módulos Python del paquete ``irpf`` al
``site_dir`` tras el build, para que Pyodide los cargue desde el navegador
sin duplicar la fuente en el repo.
"""

from __future__ import annotations

import shutil
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parents[2] / "irpf"
MODULES = ("params.py", "inflation.py", "core.py")


def on_post_build(config, **kwargs):
    dest = Path(config["site_dir"]) / "assets" / "pyodide"
    dest.mkdir(parents=True, exist_ok=True)
    for mod in MODULES:
        shutil.copy2(PACKAGE_DIR / mod, dest / mod)
