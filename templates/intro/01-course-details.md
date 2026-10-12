---
title: Course Details and System Requirements
key: details
description: Who the course is for, what you can do at the end, how it is laid out, and what your machine needs to run its labs.
estimated_duration: 5m
---
# Course Details and System Requirements

## Who this course is for

{% if training.audience %}
{{ training.audience }}
{% else %}
Anyone who wants hands-on practice with {{ certification.name or training.title }}. You should be comfortable on a command line and with the basics of Kubernetes: pods, deployments, services and namespaces.
{% endif %}

{% if training.outcomes %}
## What you can do at the end

{% for outcome in training.outcomes %}
- {{ outcome }}
{% endfor %}
{% endif %}

## How the course is laid out

Each section starts with an overview, then works through its modules. A module is a short reading, split into parts when a topic needs depth, followed by a **playground** to explore freely and, for most modules, a **graded lab** that checks your work. Each section closes with a **capstone lab** that ties its modules together.

{% if training.verified_with %}
Everything in this course was built and checked against: {{ training.verified_with | join(", ") }}.
{% endif %}

## System requirements

The labs run a real Kubernetes cluster on your own machine, inside containers.

- **A computer** running macOS or Linux (Windows through WSL 2), with at least **4 CPU cores and 8 GB of free memory** for one lab cluster, and around 20 GB of free disk space.
- **A container engine:** Docker or Podman. The cluster runs inside it.
- **`kind`:** runs Kubernetes inside the container engine.
- **`kubectl`:** talks to the cluster.
{% for tool in training.tools %}
- **`{{ tool.name }}`**{% if tool.why %}: {{ tool.why }}{% endif %}{% if tool.install %} — [install it]({{ tool.install }}){% endif %}.
{% endfor %}
- **The [Astrona command-line tool](https://github.com/astrona-io/astrona-cli)**, which starts, checks and removes every lab.

Let `astrona` check the rest for you. It shows each step it would take and asks before it changes anything:

```sh
astrona setup
astrona check
```

Then sign in once, so your lab time and results reach your account:

```sh
astrona login
```
