import os
import requests
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()
TOKEN = os.getenv("HUBSPOT_TOKEN")
FORM_ID = "924d72ee-3bb4-4f76-a9c7-4a129518fa91"

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# 1. Obtener definición del formulario (label ↔ name)
label_map = {}
url_form = f"https://api.hubapi.com/forms/v2/forms/{FORM_ID}"
resp = requests.get(url_form, headers=HEADERS, timeout=30)
resp.raise_for_status()
form_def = resp.json()

for group in form_def.get("formFieldGroups", []):
    for field in group.get("fields", []):
        label_map[field["name"]] = field.get("label", field["name"])

# 2. Descargar submissions
all_fields_found = set()
after = None
url_submissions = f"https://api.hubapi.com/form-integrations/v1/submissions/forms/{FORM_ID}"

while True:
    params = {"limit": 50}
    if after:
        params["after"] = after

    r = requests.get(url_submissions, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    for sub in data.get("results", []):
        for f in sub.get("values", []):
            all_fields_found.add(f["name"])

    after = data.get("paging", {}).get("next", {}).get("after")
    if not after:
        break

# 3. Mostrar resultado
print("\n📋 Campos encontrados en submissions:\n")
for name in sorted(all_fields_found):
    etiqueta = label_map.get(name, "(No está definido en el formulario)")
    print(f"{etiqueta:<55} → {name}")
