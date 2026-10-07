#!/usr/bin/env python3
"""Check every content file before it is merged: schema, file-name slugs, and
child keys that the sync matches on (they must be unique within a page).

    python3 scripts/validate.py          # needs PyYAML and jsonschema
"""

import json
import pathlib
import sys

import jsonschema
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
schema = json.loads((ROOT / "schema/program-page.schema.json").read_text())
validator = jsonschema.Draft202012Validator(schema)

errors = []
files = sorted((ROOT / "program-pages").glob("*.y*ml"))
for path in files:
    slug = path.stem
    try:
        page = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        errors.append(f"{path.name}: not valid YAML: {exc}")
        continue
    for err in validator.iter_errors(page or {}):
        where = "/".join(str(p) for p in err.absolute_path) or "(top)"
        errors.append(f"{path.name}: {where}: {err.message}")
    if not isinstance(page, dict):
        continue
    if page.get("slug") not in (None, slug):
        errors.append(f"{path.name}: slug {page['slug']!r} does not match the file name")
    if not jsonschema.Draft202012Validator({"pattern": schema["properties"]["slug"]["pattern"]}).is_valid(slug):
        errors.append(f"{path.name}: file name must be a slug (lowercase letters, digits, dashes)")
    keys = [(e.get("key") or e.get("short_name") or e.get("name", "")).strip().lower() for e in page.get("entries", [])]
    titles = [h.get("title", "").strip().lower() for h in page.get("highlights", [])]
    for label, values in (("entry key", keys), ("highlight title", titles)):
        for dupe in sorted({v for v in values if values.count(v) > 1}):
            errors.append(f"{path.name}: duplicate {label} {dupe!r} — the sync matches on it, so it must be unique")

if errors:
    print("\n".join(errors))
    print(f"\n{len(errors)} problem(s) in {len(files)} file(s)")
    sys.exit(1)
print(f"{len(files)} program page(s) valid")
