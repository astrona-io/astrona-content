---
# Used as <!-- astrona:playground:destroy --> in any course page — typically on a
# module's summary page, to clean up before moving on.
description: How to end a playground with astrona destroy, and what it does.
---
::snippet-card{art="destroy"}
**Done here? Bring the playground home before you move on:**

```bash
astrona destroy
```

It removes the playground's cluster from your machine, frees the memory and disk it used, and stops its clock — **that is what logs your time** on your account, so this session counts towards your hands-on hours.

Skip it and the playground keeps running until its time limit, then it is removed anyway — but that session's time is not counted. Starting the next module's playground? Destroy this one first, so the two don't compete for your machine.
::
