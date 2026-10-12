---
title: Meet Your Instructors
key: instructors
description: The crew that writes, tests and maintains this course.
estimated_duration: 2m
---
# Meet Your Instructors

{% if training.crew %}
{% for group in training.crew %}
## {{ group.title }}

{% for person in group.members %}
- **{{ person.name }}**{% if person.github %} ([@{{ person.github }}]({{ person.url }})){% elif person.url %} ([profile]({{ person.url }})){% endif %}{% if person.company %}, {{ person.company }}{% endif %}{% if person.role %} — {{ person.role }}{% endif %}

{% endfor %}
{% endfor %}
{% else %}
The crew of this course has not introduced itself yet.
{% endif %}

## Everyone who has helped

Every person who has changed this course — a typo, a lab, a whole section — is on its [contributors page]({{ training.contributors_url }}). Your name can be next: see *Course Support and Other Resources* for how to send a fix.
