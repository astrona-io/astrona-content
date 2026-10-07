# astrona-content

The content behind [astrona.io](https://astrona.io), kept as plain YAML so anyone
can read it, suggest a change, and reuse it. Today that is the **program
pages** — the ecosystem landscapes (`/cncf-landscape`, `/landscape/apache`, …)
and the certification paths (`/kubestronaut`, `/golden-kubestronaut`). More
kinds of content will follow in their own folders.

Git is the source of truth. When a pull request is merged to `main`, the
content sync service applies it to the site's database; edits made directly in
the admin app show up as *drift* until they land here.

## Layout

```
program-pages/<slug>.yaml          one page; the file name is its URL slug
schema/program-page.schema.json    every field, with what it does
scripts/validate.py                the check CI runs on every pull request
```

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

## Contributing

1. Edit or add a file under `program-pages/`.
2. Check it: `pip install pyyaml jsonschema && python3 scripts/validate.py`.
3. Open a pull request. CI runs the same check; a maintainer merges, and the
   site updates within a minute.

## Working with a local Astrona stack

From the [astrona-agent-development](https://github.com/astrona-io/astrona-agent-development)
workspace, with this repo cloned under `repos/`:

```sh
./bin/astrona-agent content drift      # what differs between this repo and your local database
./bin/astrona-agent content sync       # apply it (asks nothing; --dry-run to preview)
./bin/astrona-agent content export     # write your local database back into these files
```
