---
title: PromQL
summary: >-
  PromQL is the query language used by Prometheus to read and analyze time-series metrics.
published: true
published_at: '2026-03-14T06:12:52.228237Z'
---

## What PromQL works with

Prometheus stores metrics as time series, where each metric has:

- a name
- a value over time
- optional labels such as `job`, `instance`, `namespace`, or `pod`

Example metric:
```promql
http_requests_total{job="api", status="500"}
```

This means:
- metric name: `http_requests_total`
- labels: `job="api"` and `status="500"`

## What you can do with PromQL

PromQL can:
- select metrics
- filter by labels
- calculate rates over time
- aggregate values
- compare and combine metrics
- work with histograms and quantiles

## Why PromQL matters

PromQL is used for:
- dashboards in Grafana
- alerts in Prometheus alerting rules
- troubleshooting
- capacity and performance analysis

## Easy way to think about it

<!-- plaintext -->
SQL is for databases.
PromQL is for monitoring metrics.

It is the language that helps you turn raw Prometheus metrics into something useful for graphs, alerts, and analysis.
