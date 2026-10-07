# astrona-content

The data behind [astrona.io](https://astrona.io), kept as plain YAML so anyone
can read it, suggest a change, and reuse it. Each kind of data has its own
top-level folder:

- **program pages**: the ecosystem landscapes (`/cncf-landscape`,
  `/landscape/apache`, …) and the certification paths (`/kubestronaut`,
  `/golden-kubestronaut`);
- **knowledge hub**: the sections, topics and articles under `/knowledge-hub`.

More kinds will follow as sibling folders.

Git is the source of truth. When a pull request is merged to `main`, the
content sync service applies it to the site's database; edits made directly in
the admin app show up as *drift* until they land here.

## Layout

```
<kind>/<id>.yaml                   one record of that kind; the file name is its id
schema/<kind>.schema.json          every field of that kind, with what it does
scripts/validate.py                the check CI runs on every pull request
```

| Folder | Kind | Synced into |
| --- | --- | --- |
| `program-pages/` | landscapes and certification paths (file name = URL slug) | content service |
| `knowledge-hub/` | sections, topics, Markdown articles, related-article groups | knowledge-hub service |

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
