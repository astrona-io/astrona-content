---
title: SLO (Service Level Objective)
summary: >-
  In observability, SLO (Service Level Objective) is the target value you set for a service-level measurement.
published: true
published_at: '2026-03-14T07:20:54.940648Z'
---

## In observability eyes

From an observability perspective, an SLO is the reliability target your team monitors and works toward.<br />
<br />
It helps engineering teams focus on what matters most for the user experience instead of watching every possible metric.<br />
<br />
Example:
- SLI = percentage of successful API requests
- SLO = 99.95% successful API requests over 30 days

Observability tools are then used to measure whether the service is meeting that objective.

## Relationship to SLA and SLI

**SLA**<br />
What you promised to the customer<br />
<br />
**SLO**<br />
The target your team aims to achieve<br />
<br />
**SLI**<br />
The actual measured value<br />
<br />
Example:
- SLA = 99.9% uptime per month
- SLO = 99.95% uptime target internally
- SLI = measured uptime from monitoring data

## Why SLO matters

SLOs are important because they turn reliability into something measurable and actionable.<br />
<br />
They help teams:
- define what “good enough” means
- alert on meaningful issues
- avoid over-engineering
- use error budgets to balance reliability and feature delivery

Without an SLO, observability can become just a big collection of metrics without a clear goal.

## Easy way to think about it

- SLA = promise
- SLO = target
- SLI = measurement
