---
title: Flannel
summary: >-
  Flannel is a simple Kubernetes CNI plugin that gives Pods network connectivity across nodes by creating
  an overlay or routed network, making cluster communication easy to understand and operate.
published: true
published_at: '2026-03-14T11:01:56.239105Z'
---

## What Flannel Is

Flannel is a lightweight CNI solution for Kubernetes. Its main job is to make sure Pods can talk to each other, even when they run on different nodes.<br />
<br />

In Kubernetes, each Pod should get its own IP address, and that IP should be reachable from other Pods in the cluster. Flannel helps provide that Pod-to-Pod network.<br />
<br />

Flannel is often chosen because it is:
- simple to install
- easy to understand
- lightweight compared to more feature-rich CNIs

Practical context: Flannel matters because Kubernetes networking is one of the core building blocks of a working cluster. Without a CNI, Pods may start, but they will not communicate correctly across nodes.

## How Flannel Works

Flannel creates a cluster-wide Pod network by assigning each node its own subnet. Then it makes sure traffic is forwarded correctly between those subnets.<br />
<br />

A simplified example:
- Node A gets 10.244.1.0/24
- Node B gets 10.244.2.0/24

If a Pod on Node A wants to talk to a Pod on Node B, Flannel helps route or encapsulate that traffic so it reaches the right destination.<br />
<br />

Flannel itself focuses mainly on network connectivity. It does not try to be a full security or policy platform.<br />
<br />

Simple example:
- Pod A: 10.244.1.10
- Pod B: 10.244.2.15

Even though the Pods are on different nodes, they should still be able to communicate over the cluster network.<br />
<br />

This is the core promise of a CNI like Flannel: each Pod gets an IP, and Pod networking works consistently across the cluster.

## Backend Modes and Traffic Handling

Flannel supports different backend modes for how traffic moves between nodes. The most commonly discussed ones are:<br />
<br />

**VXLAN**<br />
This is the most common Flannel mode. It wraps Pod traffic inside another packet so it can travel between nodes over the underlying network.<br />
<br />

Why it is useful:
- easy to deploy
- works well in many environments
- does not require complex physical network setup

Trade-off:
- encapsulation adds some overhead

**host-gw**<br />
This mode uses routing instead of overlay encapsulation. It can be faster and simpler, but it usually requires that nodes can directly reach each other on the underlying network.<br />
<br />

Why it is useful:
- lower overhead than VXLAN
- simpler packet path in the right environment

Trade-off:
- less flexible in many cloud or mixed network setups

In practice, many beginners start with VXLAN, because it works in more environments with fewer network assumptions.

## What Flannel Does Well — and What It Does Not

Flannel is good at one main thing: basic Kubernetes Pod networking.<br />
<br />

It is a strong fit when you want:
- a simple cluster network
- low operational complexity
- a beginner-friendly starting point

But Flannel does not try to solve everything.<br />
<br />

Things Flannel is not known for compared with more advanced CNIs:
- advanced NetworkPolicy handling
- deep observability features
- service mesh features
- eBPF-based networking optimizations

That means Flannel is often a good choice for:
- labs
- learning environments
- small to medium simple clusters
- clusters where simplicity matters more than advanced policy control

Anti-pattern: choosing Flannel while expecting it to deliver the same policy and security capabilities as Cilium or Calico can lead to confusion later.

## Simple Example in a Kubernetes Cluster

A very common sign of Flannel in a cluster is a Pod CIDR like `10.244.0.0/16`, especially in kubeadm-based examples.<br />

You might inspect the Flannel Pods like this:
```bash
kubectl get pods -n kube-flannel
```

This shows whether the Flannel components are running in their namespace.<br />
<br />

Explanation: if these Pods are not healthy, cross-node Pod communication may fail.<br />
<br />

You can also check node information:
```bash
kubectl get nodes -o wide
```

This helps you see the cluster nodes and verify general cluster health alongside networking checks.<br />
<br />

Explanation: this does not prove Flannel is working by itself, but it helps confirm the nodes are ready and part of the cluster.<br />
<br />

A practical test is to run test Pods and try communication between them:

```bash
kubectl run test-a --image=busybox --restart=Never -- sleep 3600
kubectl run test-b --image=busybox --restart=Never -- sleep 3600
```

Explanation: these Pods can be used as temporary test workloads to validate networking.<br />
<br />

Then test connectivity:
```bash
kubectl exec -it test-a -- ping <pod-ip-of-test-b>
```

Explanation: if the ping works, Pod-to-Pod networking is functioning. If it fails across nodes, the CNI setup is one of the first areas to investigate.

## Common Mistakes and Operational Gotchas

**Expecting NetworkPolicy support by default**<br />
Flannel is mainly about connectivity, not advanced traffic policy. If your goal is strong network segmentation, Flannel alone may not meet that need.<br />
<br />

**Overlooking the Pod CIDR setup**<br />
If the Kubernetes cluster is initialized with a Pod CIDR that does not match the Flannel configuration, networking problems can appear early.<br />
<br />

Example from kubeadm-style setup:

```bash
kubeadm init --pod-network-cidr=10.244.0.0/16
```

Explanation: this CIDR is commonly used with Flannel. If the cluster CIDR and Flannel expectations do not align, Pod networking may break.<br />
<br />

**Debugging only Services, not the CNI**<br />
When apps cannot talk, people often blame Kubernetes Services first. But sometimes the real issue is simpler: Pods on different nodes cannot reach each other because the CNI is unhealthy.<br />
<br />

**Using Flannel where advanced features are required**<br />
If you already know you need fine-grained policy, rich observability, or advanced performance tuning, starting with Flannel may create migration work later.
