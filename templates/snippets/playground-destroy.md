---
description: End the current playground and clean up its temporary resources.
---
::snippet-card{art="destroy"}
**End this playground before starting another module.** Use `astrona list` to identify its environment name, then pass that name to `astrona destroy`. This removes its cluster and temporary workload data. Keep any observations you need before removal.

Stop host-side port forwards and remove temporary practice files you created. Host image caches and saved files have separate lifetimes and can remain after cluster removal. A separately launched graded lab also has its own environment and needs its own cleanup.
::
