---
title: Cilium
summary: >-
  Cilium is a modern Kubernetes CNI that connects pods, secures traffic, and adds observability using
  eBPF. It matters because networking, security, and visibility are core parts of running Kubernetes reliably.
published: true
published_at: '2026-03-14T09:13:11.570468Z'
---

## What Cilium is and why it matters

Cilium is a Container Network Interface (CNI) for Kubernetes. A CNI is the component that gives pods IP addresses and makes pod-to-pod communication work.<br />
<br />

What makes Cilium different is that it uses eBPF inside the Linux kernel. That allows it to handle networking and security in a fast and flexible way without relying as heavily on older patterns like large iptables rule sets.<br />
<br />

In practice, teams often choose Cilium because they want:
- pod networking
- network security policies
- service load balancing
- traffic visibility and troubleshooting
- a cleaner path toward advanced Kubernetes networking

So Cilium is not only “the thing that connects pods.” It often becomes a broader networking and security layer for the cluster.

## How Cilium works in simple terms

When a pod starts, Cilium helps attach that pod to the cluster network and gives it connectivity to other pods and services.<br />
<br />

At a high level, Cilium does three important jobs:
- **Networking**<br />It makes sure pods can send traffic to each other across nodes.
- **Security**<br />It can enforce rules about which pods are allowed to talk to which other pods.
- **Observability**<br />It can show who is talking to whom, which helps with debugging and security reviews.

A simple mental model is this:
- Kubernetes decides what should exist
- Cilium helps control how traffic flows between those things

For example:
- A frontend pod calls a backend service
- Cilium helps route the traffic
- Cilium can also check whether that communication is allowed
- Cilium can report that the flow happened

That combination is one reason Cilium is popular in modern platform engineering.

## Cilium and eBPF

The keyword most people connect with Cilium is eBPF.<br />
<br />

eBPF is a Linux kernel technology that lets software run small programs safely inside the kernel. Cilium uses that to make decisions about networking and security closer to where packets are actually handled.<br />
<br />

Why that matters:
- fewer legacy networking layers in some scenarios
- better performance characteristics in many environments
- more detailed visibility into traffic
- more flexible policy enforcement

You do not need to be an eBPF expert to use Cilium. But it helps to understand this basic idea:
- Cilium uses eBPF to move important networking and security logic closer to the Linux kernel.

That is why people often describe Cilium as more than just a “basic Kubernetes CNI.”

## Core features you will meet first

**Pod networking**<br />
Like any CNI, Cilium provides pod networking so workloads can communicate across the cluster.<br />

**Network policies**<br />
Cilium can enforce Kubernetes NetworkPolicy, and it also provides richer policy options through Cilium-specific resources.<br />
<br />

Example of a simple Kubernetes network policy:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: demo
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
```

This example says that pods labeled `frontend` are allowed to send traffic to pods labeled `backend` in the same namespace.<br />
<br />

That is useful when you want to reduce unnecessary east-west traffic between applications.<br />
<br />

**Service load balancing**<br />
Cilium can also handle Kubernetes service load balancing, helping traffic reach the correct backend pods.<br />
<br />

**Observability with Hubble**<br />
Cilium is often paired with Hubble, which gives visibility into network flows.<br />

Example:

```bash
hubble observe
```

This command shows live traffic flows seen by Cilium.<br />
<br />

That helps beginners and operators answer questions like:
- Which pod is calling this service?
- Is traffic being dropped?
- Are policies blocking communication?

**A practical example: why teams use Cilium**<br />
<br />

Imagine a small application with three parts:
- frontend
- api
- database

You want the following behavior:
- frontend can call api
- api can call database
- frontend must not call database directly

Cilium helps in two ways:
- It provides the networking so all pods can technically exist and communicate
- It enforces policy so only the approved paths are allowed

This is practical because Kubernetes clusters often grow quickly. Without network controls, many workloads can talk too freely to each other, which increases risk and makes troubleshooting harder.<br />
<br />

Cilium becomes valuable when you want networking to be:
- functional
- visible
- secured

That is especially important in clusters running many teams, many namespaces, or sensitive workloads.

## Common mistakes and anti-patterns

**Treating Cilium as “just another CNI”**<br />
Cilium can do much more than basic pod networking. If you only install it and never use its policy or observability features, you may miss a lot of its value.<br />
<br />

**Enabling policies without understanding defaults**<br />
A common mistake is to apply network policies without realizing how traffic changes afterward. Some workloads may suddenly lose access they depended on.<br />
<br />

A safer approach is:
- understand existing traffic first
- observe flows
- then introduce policies gradually

**Not using observability during troubleshooting**<br />
When connectivity breaks, people often jump straight to blaming DNS, Ingress, or the application. Sometimes the real issue is a dropped network flow or a policy rule.<br />
<br />

Tools like Hubble can make that much easier to see.<br />
<br />

**Mixing too many network concepts at once**<br />
<br />
Beginners often confuse these layers:
- CNI
- Ingress
- Service
- NetworkPolicy
- Service mesh

Cilium mainly lives in the networking and security space at the pod and service traffic level. It does not automatically replace every other Kubernetes networking concept.
