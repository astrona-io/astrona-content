Before hands-on work, renew the current module's playground if it was started
as a timed catalog session. Use `astrona run renew` with that playground's
catalog name or environment name from `astrona list`. Renewal keeps its cluster
and changes in place while restarting its allowed timer. An expired environment
must be started again. A local author environment without a timed session does
not need catalog renewal.
