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
