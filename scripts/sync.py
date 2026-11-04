"""Copy the open dataset from mexsaas.com into this repository and rebuild its README, citation and metadata.

Run from the repository root:  python scripts/sync.py [--kaggle-dir build/kaggle]
Only the Python standard library is used. Exits non-zero, without touching any file, when the
download fails or the data looks wrong, so a bad day on the site never empties the mirror.
"""

import argparse
import csv
import io
import json
import os
import shutil
import sys
import time
import urllib.request

BASE = os.environ.get("MEXSAAS_BASE", "https://www.mexsaas.com")
HF_REPO = os.environ.get("HF_REPO") or "mexsaas/software-usado-en-mexico"
KAGGLE_ID = os.environ.get("KAGGLE_DATASET") or "mexsaas/software-usado-en-mexico"
MIN_ROWS = 100  # the directory has had more than this since October 2026; fewer means something broke
USER_AGENT = "mexsaas-datos-sync/1.0 (+https://www.mexsaas.com/datos)"
BOM = "﻿"


def fetch(path: str) -> bytes:
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(BASE + path, headers={"user-agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as res:
                return res.read()
        except OSError as err:  # network errors and HTTP errors both land here
            last = err
            time.sleep(5 * (attempt + 1))
    raise SystemExit(f"could not download {path}: {last}")


def size_category(rows: int) -> str:
    return "n<1K" if rows < 1_000 else "1K<n<10K" if rows < 10_000 else "10K<n<100K"


def columns_table(fields: list) -> str:
    lines = ["| Columna | Qué significa |", "| --- | --- |"]
    lines += [f"| `{f['name']}` | {f['description'].replace('|', '/')} |" for f in fields]
    return "\n".join(lines)


def citation(version: str) -> str:
    return f"""cff-version: 1.2.0
message: "Si usas estos datos, cita la fuente con un enlace a mexsaas."
type: dataset
title: "Software usado en México: directorio abierto de mexsaas"
authors:
  - name: mexsaas
    website: "https://www.mexsaas.com"
url: "https://www.mexsaas.com/datos"
repository: "https://github.com/mexsaas/datos"
license: CC-BY-4.0
version: "{version[:7]}"
date-released: "{version[:10] if len(version) >= 10 else version + '-01'}"
keywords:
  - mexico
  - software
  - saas
  - precios
  - pymes
"""


def kaggle_metadata(package: dict, rows: int) -> dict:
    fields = package["resources"][0]["schema"]["fields"]
    return {
        "title": "Software usado en México (mexsaas)",
        "subtitle": "Productos de software en México con categoría y precio en pesos",
        "id": KAGGLE_ID,
        "licenses": [{"name": "CC-BY-4.0"}],
        "description": (
            f"{package['description']}\n\n{rows} productos, datos al {package['version']}. "
            "Se actualiza cada semana desde https://www.mexsaas.com/datos.\n\n"
            "Licencia CC BY 4.0: cita la fuente con un enlace a https://www.mexsaas.com/datos."
        ),
        "resources": [
            {
                "path": "software.csv",
                "description": "Un producto por fila. Listas separadas por |; si/no para los valores booleanos.",
                "schema": {"fields": [{"name": f["name"], "description": f["description"]} for f in fields]},
            },
            {"path": "software.json", "description": "Los mismos datos en JSON."},
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kaggle-dir", help="also write a Kaggle upload folder here")
    args = parser.parse_args()

    package = json.loads(fetch("/datos/datapackage.json"))
    data_json = json.loads(fetch("/datos/software.json"))
    csv_text = fetch("/datos/software.csv").decode("utf-8")
    if csv_text.startswith(BOM):
        csv_text = csv_text[1:]  # the site keeps the BOM for Excel; dataset tools read plain UTF-8

    fields = package["resources"][0]["schema"]["fields"]
    reader = list(csv.reader(io.StringIO(csv_text)))
    header, rows = reader[0], len(reader) - 1
    expected = [f["name"] for f in fields]
    if header != expected:
        raise SystemExit(f"CSV header does not match datapackage.json: {header} != {expected}")
    if rows < MIN_ROWS:
        raise SystemExit(f"only {rows} rows (minimum {MIN_ROWS}); not updating the mirror")
    if data_json.get("total") != rows:
        raise SystemExit(f"JSON total {data_json.get('total')} != CSV rows {rows}")

    version = package["version"]
    resource = package["resources"][0]
    resource.update(path="data/software.csv", encoding="utf-8")
    package["resources"].append({"name": "software-json", "path": "data/software.json", "format": "json", "mediatype": "application/json"})

    os.makedirs("data", exist_ok=True)
    with open("data/software.csv", "w", encoding="utf-8", newline="") as f:
        f.write(csv_text)
    with open("data/software.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(data_json, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open("datapackage.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(package, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open("CITATION.cff", "w", encoding="utf-8", newline="\n") as f:
        f.write(citation(version))

    with open("README.tpl.md", encoding="utf-8") as f:
        readme = f.read()
    for key, value in {
        "size_category": size_category(rows),
        "rows": str(rows),
        "version": version,
        "hf_repo": HF_REPO,
        "columns_table": columns_table(fields),
    }.items():
        readme = readme.replace("{{" + key + "}}", value)
    if "{{" in readme:
        raise SystemExit("README.tpl.md has a placeholder sync.py does not fill")
    with open("README.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(readme)

    if args.kaggle_dir:
        os.makedirs(args.kaggle_dir, exist_ok=True)
        shutil.copy("data/software.csv", os.path.join(args.kaggle_dir, "software.csv"))
        shutil.copy("data/software.json", os.path.join(args.kaggle_dir, "software.json"))
        with open(os.path.join(args.kaggle_dir, "dataset-metadata.json"), "w", encoding="utf-8") as f:
            json.dump(kaggle_metadata(package, rows), f, ensure_ascii=False, indent=2)

    print(f"ok: {rows} rows, data as of {version}")


if __name__ == "__main__":
    sys.exit(main())
