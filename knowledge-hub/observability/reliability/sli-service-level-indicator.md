---
title: SLI (Service Level Indicator)
summary: >-
  In observability, SLI (Service Level Indicator) is the actual measured metric used to show how well
  a service is performing.
published: true
published_at: '2026-03-14T07:17:48.875605Z'
---

## In observability eyes

From an observability perspective, an SLI is the signal you collect from your systems to understand user-facing reliability.

Examples of SLIs:

- percentage of successful HTTP requests
- percentage of requests served under 300 ms
- percentage of time a service is available
- number of failed requests vs total requests

Example:

```
99.97% of requests succeeded in the last 30 days
```

That could be an SLI.

## Relationship to SLA and SLO

**SLA**
What you promised

**SLO**
What target you aim for

**SLI**
What you actually measure

Example:
- SLA = 99.9% uptime per month
- SLO = 99.95% uptime target internally
- SLI = measured uptime from probes/metrics/logs

## Why SLI matters

SLIs are important because they connect observability data to real service quality.

Without SLIs, you may collect lots of metrics, but not know which ones actually reflect the user experience.

A good SLI should measure something meaningful to the user, not just internal system activity.

For example:
- good SLI = successful API requests
- less useful alone = CPU usage on one pod

CPU can help with troubleshooting, but it is not always a service-level indicator.

## Common SLI examples

**Availability SLI**
How often the service is reachable

**Latency SLI**
How fast the service responds

**Error-rate SLI**
How often requests fail

**Throughput SLI**
How much useful work the service performs

## Easy way to think about it

- SLA = promise
- SLO = target
- SLI = measured result
