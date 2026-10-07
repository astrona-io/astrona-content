---
title: SLA (Service Level Agreement)
summary: >-
  In observability, SLA (Service Level Agreement) is the formal promise made to a customer or user about
  the level of service they can expect.
published: true
published_at: '2026-03-14T07:11:44.369776Z'
---

## In observability eyes

From an observability perspective, the SLA is the target the system must live up to.<br />
<br />
Observability helps you measure and prove whether you are meeting that promise.<br />
<br />
Example:
- SLA: “The service must be available 99.9% each month”
- Then observability is used to:
- collect the availability data
- monitor downtime
- alert when reliability drops
- report whether the SLA was met

## Relationship to SLO and SLI

This is the most important way to understand it:<br />
<br />

**SLA**<br />
The promise to the customer<br />
<br />

**SLO**<br />
The internal goal used to meet the SLA<br />
<br />

**SLI**<br />
The actual measurement<br />
<br />

Example:
- SLA = “99.9% monthly uptime”
- SLO = “We aim for 99.95% uptime internally”
- SLI = the real measured uptime from metrics/logs/checks

So in practice:
- SLA is the contract
- SLO is the engineering target
- SLI is the measured value

## Why SLA matters in observability

SLA gives meaning to monitoring.<br />
<br />
Without an SLA, you may collect lots of metrics but not know what actually matters to the customer.<br />
<br />

With an SLA, observability can focus on:
- what the customer experiences
- whether the service is healthy enough
- whether the business promise is being kept

## Easy way to think about it

- SLA = what you promised
- SLO = what you aim for
- SLI = what you measure
