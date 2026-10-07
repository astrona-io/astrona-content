---
title: Labels
summary: >-
  Prometheus labels are key-value pairs attached to metrics. They add context like job, instance, or method,
  making it possible to filter, group, and query metrics across systems and services.
published: true
published_at: '2026-03-14T07:50:07.710305Z'
---

## What labels are

Labels are metadata attached to a metric as key-value pairs.
They help describe where the metric came from or what it represents.<br />
<br />
Example:
```promql
http_requests_total{job="api", instance="10.0.0.5:9090", method="GET", status="200"}
```

Here, the metric name is http_requests_total, and the labels are:
- `job="api"`
- `instance="10.0.0.5:9090"`
- `method="GET"`
- `status="200"`

## Why labels matter

Labels make Prometheus powerful because they let you:
- filter specific data
- compare dimensions
- group results
- break down metrics by service, pod, endpoint, region, status code, and more

Without labels, metrics would be much less flexible and harder to analyze.

## Common label examples

In Prometheus, every unique combination of metric name + labels becomes its own time series.<br />
<br />

Example:
```promql
http_requests_total{method="GET", status="200"}
http_requests_total{method="GET", status="500"}
http_requests_total{method="POST", status="200"}
```

These are three separate time series because the label values differ.

## Common label examples

Some common labels in Prometheus are:
- `job` → the logical service being scraped
- `instance` → the specific target being scraped
- `namespace` → Kubernetes namespace
- `pod` → Kubernetes pod name
- `method` → HTTP method
- `status` → HTTP response code

These labels help identify and organize metrics in real environments.

## Labels in queries

Labels are heavily used in PromQL to select specific data.<br />
<br />

Example:
```promql
http_requests_total{job="api"}
```

This returns only metrics where the job label is api.<br />
<br />

Example with multiple labels:
```promql
http_requests_total{job="api", status="500"}
```

This returns only failed API requests with status code 500.

## Labels for grouping

Labels are also used to group data during aggregation.<br />
<br />

Example:
```promql
sum by (status) (http_requests_total)
```

This groups request totals by HTTP status code.<br />
<br />

Another example:
```promql
sum by (pod) (container_cpu_usage_seconds_total)
```

This shows CPU usage grouped per pod.

## Good label design

Good labels should:
- describe meaningful dimensions
- be consistent across services
- use low-cardinality values when possible
- make querying easier

Good examples:
- environment
- region
- method
- status
- service

Bad examples are labels with highly unique values for every request or user.

## High cardinality warning

Too many unique label values create high cardinality, which can increase memory usage and reduce Prometheus performance.<br />
<br />

Problematic examples:
- user_id
- session_id
- request_id
- full URL paths with unique IDs

These labels can create huge numbers of time series and should usually be avoided.

## Simple takeaway

<!-- plaintext -->
Labels are what make Prometheus metrics dynamic and useful.
They turn a single metric into many meaningful time series that can be filtered, grouped, and analyzed in powerful ways.
