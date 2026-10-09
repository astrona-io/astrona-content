---
title: Course Support and Other Resources
key: support
description: How to report a mistake, how to fix one yourself, and where to read more.
estimated_duration: 3m
---
# Course Support and Other Resources

## Found a mistake? Report it

If a command fails, a page says something wrong, or a lab grades a correct answer as wrong, tell us — every report makes the course better for the next astronaut.

1. Open an issue on GitHub: [{{ training.issues_url | replace("https://", "") }}]({{ training.issues_url }}).
2. Say which page or lab it is. Every page has an *Edit this page on GitHub* link at the bottom that names its file.
3. Paste the command you ran and what you saw. Leave out passwords, tokens and anything private.
4. Say what you expected to happen instead.

Want to fix it yourself? Pull requests are welcome on [the same repository]({{ training.repository_url }}).

## When a lab misbehaves

- `astrona check` finds most problems with your machine.
- `astrona destroy` removes a lab completely; `astrona run` it again for a clean start.
- A playground stops by itself after its time limit, so a forgotten one never runs for days.

## Other resources

- **[The knowledge hub](/knowledge-hub):** short articles on the ideas behind the labs.
- **[Practice exams](/exams):** timed questions in the style of the real exam.
- **[The Astrona command-line tool](https://github.com/astrona-io/astrona-cli):** its README lists every command.
{% if certification.provider %}
- **The certification itself:** run by {{ certification.provider }} — always check their page for the current exam rules.
{% endif %}

{% if training.license %}
## License

This course is published under the [{{ training.license }}]({{ training.license_url }}) license.
{% endif %}
