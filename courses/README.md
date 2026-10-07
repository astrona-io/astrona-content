# Courses

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
