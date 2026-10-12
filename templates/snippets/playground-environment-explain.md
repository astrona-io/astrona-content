---
# Used as <!-- astrona:playground:environment-explain --> in any course page.
description: What a module's playground is, how it ends, and why destroying it counts.
---
::snippet-card{art="solar-system"}
Each playground is a training solar system in the simulator, and it is ungraded: it spins up, prepares the environment, and waits. There is no task and no `astrona submit`.

**Done? Run `astrona destroy` — that is what logs your time.** Your playground time only counts when you end it yourself. If you leave it running until its time limit (two hours, unless the module sets another), the cluster is still removed, but that session's time is not counted. Need longer? `astrona run renew` saves the time so far and starts the clock again.
::
