---
title: Vector
summary: In PromQL, a vector is a set of time series values.
published: true
published_at: '2026-03-14T06:21:41.471617Z'
---

## Instant vector

An instant vector is a set of time series at one specific point in time.

Example:
```promql
up
```

This returns the current value of `up` for all matching series right now.
So if you have 3 targets, you may get 3 results.

## Range vector

A range vector is a set of time series over a time window.

Example:
```promql
up[5m]
```

This returns all samples for `up` from the last 5 minutes for each matching series.

Range vectors are often used with functions like:

```promql
rate(http_requests_total[5m])
avg_over_time(cpu_usage[10m])
```

## Easy way to think about it

- scalar = one single number
- string = text value
- instant vector = many metric series at one moment
- range vector = many metric series across a time period

## Why it matters

You need to understand vectors because many PromQL functions only work with a specific input type.

Examples:
- `rate()` expects a range vector
- `sum()` usually works on an instant vector
- raw metric queries like `up` return an instant vector

So vectors are a core part of how PromQL works.
