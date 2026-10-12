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

# -------------------------------------------------------------------- exams --
EXAM_STATUSES = {"draft", "in_test", "published", "archived", "deprecated", "unpublished"}
EXAMS = ROOT / "exams"
exam_files = sorted(p for p in EXAMS.rglob("*") if p.is_file()) if EXAMS.is_dir() else []
exam_names: dict[str, str] = {}
for path in exam_files:
    rel = path.relative_to(ROOT).as_posix()
    parts = path.relative_to(EXAMS).parts
    if len(parts) != 2 or path.suffix not in (".yaml", ".yml"):
        errors.append(f"{rel}: not part of the exams layout (exams/<group>/<exam>.yaml)")
        continue
    if not SLUG.match(parts[0]):
        errors.append(f"{rel}: group folder {parts[0]!r} must be a slug")
    if parts[1] == "_group.yaml":
        yaml.safe_load(path.read_text())
        continue
    name = path.stem
    if not SLUG.match(name):
        errors.append(f"{rel}: {name!r} must be a slug — it is the exam's public URL")
    if name in exam_names:
        errors.append(f"{rel}: exam {name!r} is also defined in {exam_names[name]}")
    exam_names[name] = rel
    if not (EXAMS / parts[0] / "_group.yaml").exists():
        errors.append(f"{rel}: its group folder has no _group.yaml")
    exam = yaml.safe_load(path.read_text()) or {}
    if exam.get("status", "draft") not in EXAM_STATUSES:
        errors.append(f"{rel}: status must be one of {sorted(EXAM_STATUSES)}")
    domains = exam.get("domains") or []
    names = [str(d.get("name", "")).strip().lower() for d in domains]
    for dupe in sorted({n for n in names if names.count(n) > 1}):
        errors.append(f"{rel}: duplicate domain {dupe!r}")
    if domains and sum(int(d.get("weight", 0)) for d in domains) != 100:
        errors.append(f"{rel}: domain weights add up to {sum(int(d.get('weight', 0)) for d in domains)}, not 100")

# ----------------------------------------------------------------- partners --
# partners/<slug>.yaml: whose material a course track includes (partner_content).
PARTNERS = ROOT / "partners"
partner_schema = jsonschema.Draft202012Validator(json.loads((ROOT / "schema" / "partner.schema.json").read_text()))
partner_files = sorted(p for p in PARTNERS.glob("*.y*ml")) if PARTNERS.is_dir() else []
for path in partner_files:
    rel = path.relative_to(ROOT).as_posix()
    if not SLUG.match(path.stem):
        errors.append(f"{rel}: file name must be a slug")
        continue
    try:
        partner = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        errors.append(f"{rel}: not valid YAML: {exc}")
        continue
    for err in partner_schema.iter_errors(partner or {}):
        where = "/".join(str(p) for p in err.absolute_path) or "(top)"
        errors.append(f"{rel}: {where}: {err.message}")
partner_slugs = {p.stem for p in partner_files}
REQUIREMENTS = ("account", "subscription")

# ------------------------------------------------------------------ courses --
COURSES = ROOT / "courses"
course_files = sorted(p for p in COURSES.rglob("*") if p.is_file()) if COURSES.is_dir() else []
for path in course_files:
    rel = path.relative_to(ROOT).as_posix()
    if path.name in (".gitkeep", "README.md"):
        continue
    if path.parent != COURSES or path.suffix not in (".yaml", ".yml") or not SLUG.match(path.stem):
        errors.append(f"{rel}: courses are courses/<slug>.yaml")
        continue
    course = yaml.safe_load(path.read_text()) or {}
    track = course.get("track")
    if track is not None:
        # A pointer to a track repository: the course is built from it.
        repo = str((track or {}).get("repository", "")) if isinstance(track, dict) else ""
        if not re.fullmatch(r"(https://github\.com/|git@github\.com:)[A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}?(\.git)?/?", repo):
            errors.append(f"{rel}: track.repository must be a GitHub repository URL")
        if course.get("status", "draft") not in ("draft", "published", "archived"):
            errors.append(f"{rel}: status must be draft, published or archived")
        for number, entry in enumerate(course.get("partner_content") or [], 1):
            where = f"{rel}: partner_content {number}"
            if not isinstance(entry, dict):
                errors.append(f"{where}: must be a mapping")
                continue
            if set(entry) - {"repository", "partner", "requires", "note"}:
                errors.append(f"{where}: unknown field(s) {sorted(set(entry) - {'repository', 'partner', 'requires', 'note'})}")
            if not str(entry.get("repository", "")).startswith(("https://github.com/", "git@github.com:")):
                errors.append(f"{where}: repository must be a GitHub repository URL (a stage repository)")
            if entry.get("partner") not in partner_slugs:
                errors.append(f"{where}: partner {entry.get('partner')!r} is not a file in partners/")
            requires = entry.get("requires") or []
            if not isinstance(requires, list) or any(r not in REQUIREMENTS for r in requires):
                errors.append(f"{where}: requires lists {', '.join(REQUIREMENTS)}")
            if len(str(entry.get("note") or "")) > 300:
                errors.append(f"{where}: note is at most 300 characters")
        continue
    if course.get("partner_content"):
        errors.append(f"{rel}: partner_content is for track courses (it names stage repositories)")
    if not course.get("title"):
        errors.append(f"{rel}: needs a title")
    if any(s.get("exam_domain") for s in course.get("sections") or []) and not course.get("exam_key"):
        errors.append(f"{rel}: a section names an exam_domain but the course has no exam_key")
    for section in course.get("sections") or []:
        titles = [str(l.get("title", "")).strip().lower() for l in section.get("lessons") or []]
        for dupe in sorted({t for t in titles if titles.count(t) > 1}):
            errors.append(f"{rel}: section {section.get('title')!r} has two lessons titled {dupe!r}")

# Achievements (mission patches): one per file, achievements/<slug>.yaml.
ACHIEVEMENTS = ROOT / "achievements"
achievement_schema = jsonschema.Draft202012Validator(
    json.loads((ROOT / "schema" / "achievement.schema.json").read_text())
)
achievement_files = sorted(ACHIEVEMENTS.glob("*.y*ml")) if ACHIEVEMENTS.is_dir() else []
codes: dict[str, str] = {}
for path in achievement_files:
    rel = path.relative_to(ROOT).as_posix()
    if not SLUG.match(path.stem):
        errors.append(f"{rel}: file name must be a slug")
        continue
    try:
        item = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        errors.append(f"{rel}: not valid YAML: {exc}")
        continue
    for err in achievement_schema.iter_errors(item or {}):
        where = "/".join(str(p) for p in err.absolute_path) or "(top)"
        errors.append(f"{rel}: {where}: {err.message}")
    if isinstance(item, dict) and item.get("slug") not in (None, path.stem):
        errors.append(f"{rel}: slug does not match the file name")
    code = ((item or {}).get("ticket") or {}).get("code") if isinstance(item, dict) else None
    if code and code in codes:
        errors.append(f"{rel}: ticket code {code!r} is also used by {codes[code]}")
    elif code:
        codes[code] = rel
    exam = ((item or {}).get("rule") or {}).get("exam") if isinstance(item, dict) else None
    if exam and exam not in {f.stem for f in exam_files}:
        errors.append(f"{rel}: rule.exam {exam!r} is not a file under exams/")

total = len(files) + len(kh_files) + len(exam_files) + len(course_files) + len(achievement_files) + len(partner_files)
if errors:
    print("\n".join(errors))
    print(f"\n{len(errors)} problem(s) in {total} file(s)")
    sys.exit(1)
print(
    f"{len(files)} program page(s), {len(seen['article'])} knowledge hub article(s), "
    f"{len(exam_names)} exam(s), {len(achievement_files)} achievement(s) and {len(partner_files)} partner(s) valid"
)
