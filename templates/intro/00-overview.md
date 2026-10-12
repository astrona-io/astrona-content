---
title: Course Introduction
description: Start here — what this course trains you to do, what your machine needs, where to get help, and who builds it.
estimated_duration: 3m
---
# Course Introduction

Welcome aboard, astronaut. This is **{{ training.title }}**{% if certification.name %}, part of the training for the **{{ certification.name }}**{% if certification.code %} ({{ certification.code }}){% endif %} certification{% if certification.domain %}, domain *{{ certification.domain }}*{% endif %}{% endif %}.

{% if training.description %}
{{ training.description }}
{% endif %}

Before the first mission, three short pages get you ready:

1. **Course Details and System Requirements:** who the course is for, what you can do at the end, how it is laid out, and what your machine needs.
2. **Course Support and Other Resources:** where to ask, how to report a mistake, and where to read more.
3. **Meet Your Instructors:** the crew that builds and checks this course.

{% if sections %}
## The flight plan

| | Section | Pages | Labs |
| --- | --- | --- | --- |
{% for section in sections %}
| {{ section.label }} | {{ section.title }} | {{ section.pages }} | {{ section.labs }} |
{% endfor %}
{% endif %}

> [!TIP]
> Learning here is free and always will be. Sign in to keep your progress across devices — everything else works without an account.
