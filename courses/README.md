# Courses

A course is either written out here, or — for a **course track** — points at
a track repository that holds it:

```yaml
# courses/istio-certified-associate-ica.yaml
track:
  repository: https://github.com/astrona-io/ATP002   # any GitHub repository with a path.yaml
  ref: main
status: published          # default draft
exam_key: ica              # optional; default from the track's examPreparation.examId
```

A track's `path.yaml` (`kind: TrainingPath`) lists stages; each stage is one
exam domain and points at a repository with an `astrona.yaml` (an Astrona
training series, `ATSxxx`, or a third-party one). The content sync turns each
stage into a section and its readings, playgrounds and labs into lessons.
Pointing at a repository here is the review step that decides it may be shown
on astrona.io.

### Partner material

A stage may point at a partner's repository. Learning from it is free; running
it may not be. Say so in the course file, so the site can tell students before
they start:

```yaml
track:
  repository: https://github.com/astrona-io/ATP002
partner_content:
  - repository: https://github.com/example-org/example-training   # a stage repository of this track
    partner: example-labs                # partners/example-labs.yaml
    requires: [subscription]             # account | subscription
    note: The free tier covers the first three labs.   # optional, up to 300 characters
```

Every lesson from that repository then names the partner; its labs and
playgrounds also carry `requires`. There are two kinds: `account` (a free
account with the partner) and `subscription` (a paid one). They exist for labs
that have to run on the partner's platform — for example where the partner tests
them — instead of with the Astrona CLI. The course card ("Partner · needs an
account" / "Partner · needs a subscription"), the course page, the lesson and
`/partners` show it. A page can add its own need in its front matter
(`requires: [account]`).

## Courses written out here

One file per course: `courses/<slug>.yaml`; the file name is its URL slug
(`/courses/<slug>`). Sections and lessons are listed in order; they are matched
by title, so renaming one replaces it.

```yaml
title: CKA in practice
status: published            # draft | published | archived
exam_key: cka                # the exam it prepares for (exams/<group>/cka.yaml)
thumbnail_url: https://…
description: >-
  What the course covers.
sections:
  - title: Cluster setup
    exam_domain: Cluster Architecture, Installation and Configuration   # a domain name from the exam's file
    lessons:
      - title: kubeadm from scratch
        lesson_type: video   # video | article
        status: published    # draft | published | deactivated | coming
        video_details:
          url: https://www.youtube.com/watch?v=…
      - title: What kubeadm does
        lesson_type: article
        body_content: |
          Markdown…
```

No course has moved here yet: the first one is written here, not in the admin.
