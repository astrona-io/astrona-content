---
title: Weave Net
summary: >-
  Weave Net is a Kubernetes CNI plugin that gives Pods network connectivity across nodes using a simple
  overlay approach. It is easy to understand, but today it is best learned partly as a practical concept
  and partly as a legacy option.
published: true
published_at: '2026-03-14T09:21:22.816494Z'
---

## What Weave Net is, and why it matters

In Kubernetes, a CNI plugin is what makes Pod networking actually work. Kubernetes expects Pods to be able to communicate across nodes, but it does not provide that networking by itself. A CNI plugin fills that gap.<br />
<br />

Weave Net is one of those CNI plugins. Its job is to connect Pods on different nodes as if they were on one shared network. Historically, it became popular because it was relatively easy to install and worked well for teams that wanted simple multi-node Pod networking without needing to design everything from scratch. Today, the project is community-supported through a fork, which is important practical context when evaluating it for modern production use.<br />
<br />

A beginner-friendly way to think about it:
- Kubernetes creates Pods
- Weave Net gives those Pods IP networking
- That lets apps talk to each other across the cluster

Without a working CNI, Pods may start, but cluster networking will not behave correctly.

## How Weave Net works at a high level

<!-- plaintext -->
Weave Net mainly works by building an overlay network between Kubernetes nodes. An overlay means it creates a virtual network on top of the physical network you already have.<br />
<br />

That means:
- each node runs Weave Net
- the nodes form connections to each other
- Pod traffic can move between nodes through that virtual network

Simple example:
- Pod A runs on node-1
- Pod B runs on node-2
- Weave Net makes it possible for Pod A to reach Pod B using Pod IP networking, even though they are on different machines

This is useful because Kubernetes scheduling is dynamic. A workload may move to another node later, but the cluster still needs predictable communication.<br />
<br />

A practical reason this matters: application teams usually want to say “service A talks to service B” — not “service A can only talk if both Pods happen to be on the same server.”

## What gets installed in the cluster

Weave Net is usually deployed as a DaemonSet, meaning one Weave Net Pod runs on each Kubernetes node. That local agent handles networking tasks for that node. In Kubernetes environments, Weave Net also installs as a CNI plugin so kubelet and the container runtime can call it when Pods are created. The documentation also notes dependency on standard CNI components such as portmap for host port support.<br />
<br />

Example command:
```bash
kubectl get pods -n kube-system -o wide
```

This lets you inspect system Pods. In a cluster using Weave Net, you would typically see a Weave-related Pod running on each node.<br />
<br />

Example:
```bash
kubectl get daemonset -n kube-system
```

This helps confirm that the networking component is deployed cluster-wide.<br />
<br />

Why this matters in practice:
- if Weave Net is missing from one node, Pods on that node may have broken networking
- if the CNI setup is incomplete, kubelet may report network initialization issues
- if required helper plugins are missing, some features may not work as expected

## A simple traffic example

Imagine you deploy a frontend and a backend:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: frontend
spec:
  containers:
    - name: app
      image: nginx
---
apiVersion: v1
kind: Pod
metadata:
  name: backend
spec:
  containers:
    - name: app
      image: httpd
```

This example is intentionally simple. If frontend and backend land on different nodes, Weave Net helps provide the Pod-to-Pod network path between them.<br />
<br />

Explanation:
- Kubernetes creates the Pods
- the CNI plugin assigns networking
- Weave Net makes cross-node Pod communication possible

In real life, you would usually connect apps through a Service, not directly by Pod IP, but the underlying Pod network still has to function correctly for the cluster model to work. That network model is exactly why CNI plugins matter.

## Strengths, limitations, and where beginners get confused

**Why people liked it**<br />
Weave Net became well known because it was approachable and gave a working overlay network without requiring deep networking expertise on day one.<br />
<br />

**Limitations to understand**<br />
For modern Kubernetes learning, it is important not to treat Weave Net as “the default CNI.” Kubernetes supports many CNI plugins, and the best choice depends on compatibility, scale, security needs, performance goals, and maintenance status.<br />
<br />

**Common mistakes and anti-patterns**<br />
<br />

**Mistake 1: Thinking Kubernetes networking works without CNI**<br />
It does not. Kubernetes requires a compatible CNI plugin to implement the network model.<br />
<br />

**Mistake 2: Choosing Weave Net only because it is easy to find in old tutorials**<br />
A lot of older Kubernetes guides still mention Weave Net, but current production decisions should also consider project activity, compatibility, and operational needs. Weave Net is now community-supported rather than a mainstream actively vendor-driven default.<br />
<br />

**Mistake 3: Ignoring MTU and network overhead**<br />
Overlay networks add encapsulation overhead. If MTU is not handled well, you can see strange connectivity or performance issues. This is a common networking pain point with overlay designs. A long-running issue history around MTU and performance is one reason operators must understand the underlying network, not just install the plugin.<br />
<br />

**Mistake 4: Assuming it scales the same way in every environment**<br />
Like all CNIs, real-world behavior depends on node count, traffic patterns, and infrastructure design. Old issue discussions show that scale and stability can become operational topics in larger clusters.

## When it makes sense to learn Weave Net today

Weave Net is still worth understanding because it teaches several core Kubernetes networking ideas clearly:
- what a CNI plugin is
- how overlay networking works
- why Pod-to-Pod communication across nodes is necessary
- how cluster networking depends on node-level agents

For documentation or e-learning, Weave Net is useful as a teaching example because the mental model is simple. For new production platforms, teams usually compare it with more actively maintained alternatives and validate support for their Kubernetes version, security model, and operational goals.
