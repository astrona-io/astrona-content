# Partners

One file per partner whose material a course track includes:
`partners/<slug>.yaml`, checked against `../schema/partner.schema.json`.

```yaml
# partners/example-labs.yaml (an example — not a real partner)
name: Example Labs
url: https://example.com
logo_url: https://example.com/logo.svg   # optional
summary: Browser-based clusters for hands-on practice.
```

A partner file alone shows nothing. A course track names the stage repositories
that hold partner material in its `partner_content` (see
[`../courses/README.md`](../courses/README.md#partner-material)); the content sync
then marks those lessons, and the website says on the course, its lessons and
`/partners` that the material is **free to learn, but running it needs an
account or a subscription** with the partner — for labs that run on the
partner's platform rather than with the Astrona CLI.
