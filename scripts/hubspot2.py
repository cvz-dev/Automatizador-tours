"""
Exportar submissions de HubSpot copiando el orden de la exportación manual
Requiere: requests, openpyxl, python‑dotenv  (ya los tenías instalados)
"""

from __future__ import annotations
import os, requests
from pathlib import Path
from datetime import datetime, timezone
from openpyxl import Workbook
from dotenv import load_dotenv

# ---------- 0. Configuración ----------
load_dotenv()
TOKEN   = os.getenv("HUBSPOT_TOKEN")
FORM_ID = "924d72ee-3bb4-4f76-a9c7-4a129518fa91"
OUTPUT  = Path("../data/registros_formulario.xlsx")

SUBM_URL = f"https://api.hubapi.com/form-integrations/v1/submissions/forms/{FORM_ID}"
FORM_URL = f"https://api.hubapi.com/forms/v2/forms/{FORM_ID}"
HEADERS  = {"Authorization": f"Bearer {TOKEN}"}

# ---------- 1. Leer definición para obtener orden + labels ----------
r = requests.get(FORM_URL, headers=HEADERS, timeout=30)
r.raise_for_status()
form_def = r.json()

ordered_fields: list[str] = []
label_map: dict[str, str] = {}

for group in form_def.get("formFieldGroups", []):
    for fld in group.get("fields", []):
        name  = fld["name"]
        label = fld.get("label", name)
        ordered_fields.append(name)
        label_map[name] = label

label_map["submittedAt"] = "Fecha de envío"      # meta‑campo

# ---------- 2. Descargar TODOS los envíos ----------
rows, after = [], None
while True:
    params = {"limit": 50}
    if after:
        params["after"] = after

    r = requests.get(SUBM_URL, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    payload = r.json()

    for sub in payload.get("results", []):
        row = {
            "submittedAt": datetime
                .fromtimestamp(sub["submittedAt"]/1000, tz=timezone.utc)
                .astimezone().isoformat(timespec="seconds")
        }
        for f in sub.get("values", []):
            row[f["name"]] = f.get("value", "")
            # capturar campos nuevos no declarados en el constructor
            if f["name"] not in ordered_fields:
                ordered_fields.append(f["name"])
        rows.append(row)

    after = payload.get("paging", {}).get("next", {}).get("after")
    if not after:
        break

# ---------- 3. Ordenar filas: más reciente primero ----------
rows.sort(key=lambda r: r["submittedAt"], reverse=True)

# ---------- 4. Grabar Excel ----------
wb = Workbook()
ws = wb.active
ws.title = "Form Submissions"

header = ["submittedAt"] + ordered_fields  # submittedAt primero, luego definición
ws.append([label_map.get(c, c) for c in header])

for r in rows:
    ws.append([r.get(c, "") for c in header])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
wb.save(OUTPUT)
print(f"✅ {len(rows)} envíos guardados en {OUTPUT.resolve()}")
