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
authoring/*.md                     guides for authors of the training repositories (not synced)
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
knowledge-hub/<section>/_section.yaml            title, description, sort_order, code, color
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
sort_order: 2                   # optional: place in its topic (then title); default 0
featured: 2                     # optional: a "Start here" pick on the hub home, 1 first
certifications: [cca, cka, kcna] # optional: exams it helps with, by exam file slug
---

## What Cilium is and why it matters

Each `## heading` starts one block on the page. Use `###` and deeper inside a block.

## Notes

<!-- plaintext -->
A block whose first line is that comment is shown as plain text.
```

- Slugs are global: no two topics, and no two articles, may share one.
  `glossary`, `exam` and `search` are hub pages, so no section may use them.
- A section's `code` is its three-letter reference (`OBS`), unique and
  uppercase; entries are referred to by it (`OBS·06·02` is the second entry of
  the area's sixth topic). Its `color` (`'#ff7a18'`, quoted) is the area's
  colour on the site.
- An article's place in its topic is `sort_order`, then title; leave it out to
  keep them alphabetical. `featured` puts it in "Start here" on the hub home
  (ascending, three at most).
- `certifications` lists the exams an article helps with, by the exam's file
  name under `exams/` (`pca` for `exams/golden-kubestronaut/pca.yaml`). The hub
  gets a page per certification an article names, titled with the exam's
  `long_name`.
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

### Certification facts (`certification`)

The real certification's facts, shown on the exam page (the hero chips and the
format tooltip). Take every value from the provider's official pages: the
product page, its FAQ and its exam instructions. The pass score shown is the
exam's own `pass_score`.

```yaml
certification:
  provider: Linux Foundation
  type: multiple_choice            # multiple_choice | performance_based
  questions: 60                    # or the low end of a range…
  questions_max: 20                # …and its high end ("15–20 tasks")
  duration_minutes: 90
  delivery: online_proctored
  retakes: 1                       # free retakes included
  validity_years: 2
  price_usd: 250                   # exam-only list price
  url: https://training.linuxfoundation.org/certification/kubernetes-cloud-native-associate/
```

`schema/exam-certification.schema.json` is the block's shape.

### Hands-on exams (`lab_exam`)

An exam file may add a `lab_exam` block: the exam then offers a hands-on exam,
a timed set of labs drawn by domain weight from the training repositories
(`astrona-io/ATS*`) and run on the student's machine.

```yaml
lab_exam:
  tasks: { min: 15, max: 20 }      # an attempt draws this many labs (1–30)
  time_limit_minutes: 120          # 30–300
  break_minutes: 15                # the longest one break may last (1–30)
  clusters:
    count: 4                       # kind clusters built before the clock starts (1–6)
    kind:                          # the profile each is built from, as a lab's runtime.kind
      nodes: { controlPlanes: 1, workers: 1 }   # no addons: kind's default CNI, kindnet
  # pass_score and max_breaks default to the exam's own
```

A lab joins the pool when its training names this exam in
`training.certification`, its entry in `astrona.yaml` sets
`examScope: namespace` or `examScope: cluster`, it is not a capstone, and its
kind config fits the profile (same node counts and CNI, addons a subset).
After each sync the content sync checks that every domain has enough eligible
labs for its share at `tasks.max`; until it does, the exam is sent as
unavailable and the sync reports which domain is short: as an error once the
exam's `status` is `published`, as a warning before that.
`schema/lab-exam.schema.json` is the block's shape.

A lab must be written for it first, in ATS020's format: its own namespaces,
a context guard that reads `ASTRONA_KUBE_CONTEXT`, one
`validation/validate-<outcome>.sh` grader per outcome with points,
`astrona test` proving every outcome fails at the start and passes after the
solution, and an `Allow about N minutes for the tasks.` line.
See [`authoring/exam-ready-labs.md`](authoring/exam-ready-labs.md).

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
and the twelve earned last (Explore shows the rest):
`achievements/<slug>.yaml`, checked against `schema/achievement.schema.json`.

```yaml
title: "Ten Successful Missions"
how: "Pass ten graded labs."          # shown while not yet earned
order: 21                             # earned ones come first, then this order
ticket: { code: L10, theme: green }   # the patch: code up to 8 characters, unique; theme: blue, gold, green, cyan, orange, violet
rule: { kind: labs_passed, at_least: 10 }
```

Rule kinds, all worked out from data the services already keep (nothing is stored
per student for a ticket): `lessons_completed` (different lessons finished, each once),
`updated_lessons_read` (a lesson finished again after its text changed — once per
update, to bring readers back to what changed), `sections_completed`, `courses_completed` (every lesson
done; `course: <slug>` narrows it to one course, by its file name under `courses/`),
`labs_passed` (graded labs passed with `astrona submit`), `labs_started` (graded labs
begun with `astrona run`, pass or not),
`playgrounds_started` (playgrounds launched; renewing one with `astrona run renew` is not
a new launch), `playground_renews` (renews used), `playground_hours` (counted
playground time — ended with `astrona destroy` or renewed), `lab_hours` (counted lab
time — a lab counts once it passes), `cockpit_hours` (labs and playgrounds together),
`mock_exams` (multiple-choice exams; `level`, `exam` and `passed` narrow it),
`lab_exams` (graded full hands-on lab exams; `exam`, `passed` and `min_score` narrow
it), `streak_days` (best streak), and the social ones from the timeline:
`likes_given` (likes you gave on other students' events), `comments_written`
(comments you wrote on other students' events, replies included), `replies_written`
(replies to another student's comment), `likes_received` (likes from others on your
events), `comments_received` (comments from others on your events), `followers`
(followers visible now — public profile, not blocked), `event_likes` (most likes from
others on any one of your events) and `event_comments` (most comments from others on
any one of your events). The social counts skip hidden comments, actions on your own
events and your own comments in your own threads; a like or comment that is removed
stops counting, but a patch already earned stays. All of these take `at_least` — and
`program` with `program: kubestronaut | golden-kubestronaut` (every certification
of the program held; its progress is certifications held out of the program's). The git sync mirrors the folder into the content service;
git owns every achievement.
