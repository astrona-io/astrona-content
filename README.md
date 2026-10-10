# astrona-content

The data behind [astrona.io](https://astrona.io), kept as plain YAML so anyone
can read it, suggest a change, and reuse it. Each kind of data has its own
top-level folder:

- **program pages**: the ecosystem landscapes (`/cncf-landscape`,
  `/landscape/apache`, …) and the certification paths (`/kubestronaut`,
  `/golden-kubestronaut`);
- **knowledge hub**: the sections, topics and articles under `/knowledge-hub`;
- **exams**: each exam's public definition (`/exams/<name>`) — name, description,
  pass score and its domains with their weights. Never the questions: question
  banks stay private;
- **courses**: the course catalogue, its sections and lessons (empty for now).

More kinds will follow as sibling folders.

Git is the source of truth. When a pull request is merged to `main`, the
content sync service applies it to the site's database; edits made directly in
the admin app show up as *drift* until they land here.

## Layout

```
<kind>/<id>.yaml                   one record of that kind; the file name is its id
schema/<kind>.schema.json          every field of that kind, with what it does
scripts/validate.py                the check CI runs on every pull request
templates/intro/*.md               the Course Introduction every course track opens with
templates/snippets/<group>-<name>.md   shared text for <!-- astrona:<group>:<name> --> in a page
```

| Folder | Kind | Synced into |
| --- | --- | --- |
| `program-pages/` | landscapes and certification paths (file name = URL slug) | content service |
| `knowledge-hub/` | sections, topics, Markdown articles, related-article groups | knowledge-hub service |
| `exams/` | exam groups (`<group>/_group.yaml`) and exams (`<group>/<exam>.yaml`) | assessment engine |
| `courses/` | one file per course — see [`courses/README.md`](courses/README.md) | course engine |
| `partners/` | whose material a course track includes — see [`partners/README.md`](partners/README.md) | no service: read into the courses that name it |

Adding a kind: a new folder, its schema, a validator entry, and an entry in the
content sync service's `KINDS` registry (folder → parser → owning service).

## A page

```yaml
kind: certification_path        # or: landscape
title: Kubestronaut Path
status: published               # draft pages are not shown
sort_order: 0                   # order among pages of the same kind
logo_url: /certs/kubestronaut.png
intro: >-
  Start here if you want to understand the Kubestronaut path …
highlights:                     # short cards above the entries, in order
  - title: Core path
    detail: Five certifications covering fundamentals, administration, …
entries:                        # the cards, in order
  - name: Kubernetes and Cloud Native Associate
    short_name: KCNA
    href: /exams/kcna
    icon_url: /certs/kcna.png
    detail: Start with cloud native fundamentals …
  - name: FluxCD               # on a landscape
    status: upcoming            # renders "Upcoming" instead of a link
```

Fields you leave out take their defaults (`status: available`,
`is_active: true` for entries). The full list is in
[`schema/program-page.schema.json`](schema/program-page.schema.json); editors
that understand JSON Schema (VS Code with the YAML extension, JetBrains) can use
it for completion.

### How the sync matches things

- A page is its file name. Renaming the file creates a new page.
- An entry is matched by `key`, else `short_name`, else `name`. To **rename**
  an entry without losing its history, add `key:` with the old name first.
- A highlight is matched by its `title`.
- The order in the file is the order on the page.
- The admin app may add its own entries and highlights to a page from here;
  they show as *Manual* and survive a sync. Git always wins: list a card with
  the same key here and it takes that card over.

## The knowledge hub

```
knowledge-hub/<section>/_section.yaml            title, description, sort_order
knowledge-hub/<section>/<topic>/_topic.yaml      title, description, sort_order
knowledge-hub/<section>/<topic>/<article>.md     one article; the file name is its URL slug
knowledge-hub/related-groups.yaml                "related articles" groups
```

An article is Markdown with front matter:

```markdown
---
title: Cilium
summary: Cilium is a modern Kubernetes CNI …
published: true                 # false keeps it off the site
published_at: '2026-03-14T09:13:11Z'
---

## What Cilium is and why it matters

Each `## heading` starts one block on the page. Use `###` and deeper inside a block.

## Notes

<!-- plaintext -->
A block whose first line is that comment is shown as plain text.
```

- Slugs are global: no two topics, and no two articles, may share one.
- Moving an article to another folder moves it on the site; renaming the file
  makes it a new article (its votes stay with the old one, which is deleted).
- `related-groups.yaml` lists groups by `title`, with `articles` (the group,
  in order) and `shown_on` (the articles whose page shows it), both as slugs.
- The admin app may add its own sections, topics, articles and groups; they
  show as *Manual* and survive a sync. Git always wins: a file with the same
  slug (a group: the same title) takes that row over.

## Exams

```yaml
# exams/kubestronaut/kcna.yaml — the file name is the exam's URL (/exams/kcna)
long_name: Kubernetes and Cloud Native Associate
status: in_test            # draft | in_test | published | archived | deprecated | unpublished
pass_score: 75
max_breaks: 3
description: …
domains:                    # in display order; weights must add up to 100
  - name: Kubernetes Fundamentals
    weight: 44
    description: …
```

Domains are matched by name: questions and course sections point at them, so
renaming a domain replaces it — and the sync refuses to remove a domain that
questions still use. An exam removed from here that has attempts or questions
is archived, not deleted.

## Contributing

1. Edit or add a file under `program-pages/` or `knowledge-hub/` — or use
   "Edit this page on GitHub" at the foot of the page on the site.
2. Check it: `pip install pyyaml jsonschema && python3 scripts/validate.py`.
3. Open a pull request. CI runs the same check; a maintainer merges, and the
   site updates within a minute.

## Working with a local Astrona stack

From the [astrona-agent-development](https://github.com/astrona-io/astrona-agent-development)
workspace, with this repo cloned under `repos/`:

```sh
./bin/astrona-agent content status     # what differs between this repo and your local database
./bin/astrona-agent content sync       # apply it (asks nothing; --dry-run to preview)
./bin/astrona-agent content export --kind knowledge-hub --write   # local database back into these files
```

## The Course Introduction (`templates/intro/`)

Every course track opens with a **Course Introduction** section built from these
templates, so the same welcome, system requirements, support and crew pages are
not written again in every training repository. `00-*.md` is the section's
overview; the other files, in file-name order, are the pages of its "Course
Introduction" module. Front matter gives a page its `title` and `key` (its URL
part), plus the usual `description` and `estimated_duration`.

The templates are [Jinja](https://jinja.palletsprojects.com/), filled per
training from its `astrona.yaml`. Optional fields under `training:` feed them:

```yaml
training:
  id: ATS014
  title: "ICA: Traffic Management"
  description: >
    …
  audience: Kubernetes engineers who are new to Istio.
  outcomes:
    - Route requests by header, URI and query parameter
    - Shift and mirror traffic safely
  tools:                       # beyond a container engine, kind, kubectl and astrona
    - name: istioctl
      why: Istio's own command-line tool
      install: https://istio.io/latest/docs/setup/getting-started/#download
    - helm
  verified_with: {istio: 1.30.5, kubernetes: 1.33}
  license: Apache-2.0          # links to the repository's LICENSE
  crew:                        # any roles; each becomes a heading on "Meet Your Instructors"
    core_maintainers:
      - {name: Paris Nakita Kejser, github: parisnakitakejser}
    reviewers:
      - {name: …, github: …, company: …}
  intro: false                 # leave the Course Introduction out
  certification: {name: …, code: …, provider: …, domain: …}
```

In a template: `training.*` (the fields above, plus `repository_url`,
`issues_url`, `contributors_url`, `license_url`; `crew` is a list of
`{title, members}`), `certification.*`, and `sections` (each `label`, `title`,
`pages`, `labs`). A training that writes its own `sections/intro/` keeps it and
gets no generated one. A template that cannot be filled is left out and named in
the sync's warnings.

## Shared snippets (`templates/snippets/`)

A line `<!-- astrona:<group>:<name> -->` in any course page is replaced by
`templates/snippets/<group>-<name>.md` when the page is synced, so text that
belongs in many pages is written once — for example
`<!-- astrona:playground:environment-explain -->` explains what a playground is,
`<!-- astrona:playground:renew -->` shows how `astrona run renew` gives a running
playground its full time limit again, and `<!-- astrona:playground:destroy -->`
— typically on a module's summary page — shows how `astrona destroy` ends the
playground, frees the machine and logs its time before the student moves on.
Snippets are Jinja with the same `training`, `certification` and `sections` as
the Course Introduction; front matter is only for notes. On GitHub the marker is
an invisible comment. An unknown snippet stays a comment and is named in the
sync's warnings.

A snippet can sit in a card with an animation beside it by wrapping its text:
`::snippet-card{art="solar-system"}` … `::` (astrona-web's
`components/mdc/SnippetCard.vue` lists the scenes: `solar-system`, `renew`, `destroy`).

## Achievements (`achievements/`)

Each file is one achievement in the student's **flight log**
(`/account/flight-log`), shown as a mission patch — tickets are kept for the
certification programs. The dashboard shows the three closest to being earned
and the twenty earned last:
`achievements/<slug>.yaml`, checked against `schema/achievement.schema.json`.

```yaml
title: "Ten Successful Missions"
how: "Pass ten graded labs."          # shown while not yet earned
order: 21                             # earned ones come first, then this order
ticket: { code: L10, theme: green }   # the patch: code up to 6 letters, unique; theme: blue, gold, green, cyan, orange, violet
rule: { kind: labs_passed, at_least: 10 }
```

Rule kinds, all worked out from data the services already keep (nothing is stored
per student for a ticket): `lessons_completed` (different lessons finished, each once),
`updated_lessons_read` (a lesson finished again after its text changed — once per
update, to bring readers back to what changed), `sections_completed`, `courses_completed` (every lesson
done), `labs_passed` (graded labs passed with `astrona submit`),
`playground_hours` (counted playground time — ended with `astrona destroy`),
`mock_exams`, `streak_days` (best streak) — each with `at_least` — and
`program` with `program: kubestronaut | golden-kubestronaut` (every certification
of the program held; its progress is certifications held out of the program's). The git sync mirrors the folder into the content service;
git owns every achievement.
