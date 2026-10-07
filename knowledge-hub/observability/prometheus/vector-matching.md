---
title: Vector matching
summary: >-
  Vector matching in PromQL is how Prometheus matches time series from one vector with time series from
  another vector when you do binary operations between them.
published: true
published_at: '2026-03-14T06:58:25.445413Z'
---

## Easy example

Let’s say you have:

```promql
http_requests_total{pod="api-1", method="GET"}
http_requests_total{pod="api-1", method="POST"}
```

and:

```promql
pod_info{pod="api-1", node="worker-1"}
```

If you combine 2 vectors, Prometheus needs rules for how `pod="api-1"` on one side matches `pod="api-1"` on the other side.<br />
<br />
That is what vector matching is for.

## The main matching types

**1. Default matching**

By default, Prometheus matches series using all shared labels.<br />
<br />
That means labels must line up correctly, or the series will not match.<br />
<br />
**2. `on(...)`**

Use `on(...)` when you want to match only on specific labels.

Example:
```promql
rate(http_requests_total[5m]) / on(pod) kube_pod_info
```

This says:
- only use `pod` to decide the match<br />
<br />

**3. `ignoring(...)`**

Use `ignoring(...)` when you want to ignore certain labels during matching.

Example:
```promql
rate(http_requests_total[5m]) / ignoring(method) some_other_metric
```

This says:
- match on everything except `method`

## One-to-one vs many-to-one

Sometimes one series on the left matches exactly one on the right.<br />
<br />
That is **one-to-one**.<br />
<br />
But sometimes many series on one side should match one series on the other.<br />
<br />
Then you use:
- group_left
- group_right<br />
<br />

`group_left`<br />
Used when the left side has more series<br />
<br />

`group_right`<br />
Used when the right side has more series<br />
<br />

Example idea:
```promql
rate(http_requests_total[5m]) * on(pod) group_left(node) kube_pod_info
```

This means:
- match on pod
- many left-side series may match one right-side series
- also keep the node label from the right side

## Why it matters

Vector matching is important when you:
- combine 2 metrics
- enrich one metric with labels from another
- divide one metric by another
- compare related metrics with different label sets

Without correct vector matching, you often get:
- no results
- wrong matches
- many-to-many matching errors
