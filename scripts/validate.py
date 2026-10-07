#!/usr/bin/env python3
"""Check every content file before it is merged.

Program pages: schema, file-name slugs, and child keys the sync matches on.
Knowledge hub: the folder layout, front matter, unique slugs, and related
groups that only name articles which exist.

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

# ------------------------------------------------------------ knowledge hub --
import re  # noqa: E402

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)
KH = ROOT / "knowledge-hub"
kh_files = sorted(p for p in KH.rglob("*") if p.is_file()) if KH.is_dir() else []
seen: dict[str, dict[str, str]] = {"section": {}, "topic": {}, "article": {}}


def note(kind, slug, rel):
    if not SLUG.match(slug):
        errors.append(f"{rel}: {slug!r} must be a slug (lowercase letters, digits, dashes)")
    if slug in seen[kind]:
        errors.append(f"{rel}: {kind} slug {slug!r} is also used by {seen[kind][slug]}")
    seen[kind][slug] = rel


def mapping(path, rel):
    try:
        data = yaml.safe_load(path.read_text()) or {}
    except yaml.YAMLError as exc:
        errors.append(f"{rel}: not valid YAML: {exc}")
        return {}
    if not isinstance(data, dict) or not data.get("title"):
        errors.append(f"{rel}: must be a mapping with a title")
        return {}
    return data


groups = []
for path in kh_files:
    rel = path.relative_to(ROOT).as_posix()
    parts = path.relative_to(KH).parts
    if parts == ("related-groups.yaml",):
        groups = yaml.safe_load(path.read_text()) or []
    elif len(parts) == 2 and parts[1] == "_section.yaml":
        mapping(path, rel)
        note("section", parts[0], rel)
    elif len(parts) == 3 and parts[2] == "_topic.yaml":
        mapping(path, rel)
        note("topic", parts[1], rel)
        if not (KH / parts[0] / "_section.yaml").exists():
            errors.append(f"{rel}: its section folder has no _section.yaml")
    elif len(parts) == 3 and path.suffix == ".md":
        note("article", path.stem, rel)
        if not (KH / parts[0] / parts[1] / "_topic.yaml").exists():
            errors.append(f"{rel}: its topic folder has no _topic.yaml")
        match = FRONT.match(path.read_text().replace("\r\n", "\n"))
        meta = yaml.safe_load(match.group(1)) if match else None
        if not isinstance(meta, dict) or not meta.get("title"):
            errors.append(f"{rel}: must start with front matter (--- … ---) that has a title")
    else:
        errors.append(f"{rel}: not part of the knowledge-hub layout (see README)")
for group in groups:
    for slug in [*group.get("articles", []), *group.get("shown_on", [])]:
        if slug not in seen["article"]:
            errors.append(f"knowledge-hub/related-groups.yaml: {group.get('title')!r} names unknown article {slug!r}")

total = len(files) + len(kh_files)
if errors:
    print("\n".join(errors))
    print(f"\n{len(errors)} problem(s) in {total} file(s)")
    sys.exit(1)
print(f"{len(files)} program page(s) and {len(seen['article'])} knowledge hub article(s) valid")
