---
title: Calico
summary: >-
  Calico is a Kubernetes CNI that provides pod networking and strong network policy controls, making it
  popular when you need both connectivity and security in one solution.
published: true
published_at: '2026-03-14T11:11:19.364717Z'
---

## What Calico is and why it matters

Calico is more than a basic pod network plugin. It gives Kubernetes two important things at the same time: pod-to-pod connectivity and traffic control through network policy. In practice, that means your applications can talk across nodes, and you can decide exactly which workloads are allowed to communicate. This matters because many real clusters need both reachability and isolation, not just “everything can talk to everything.”<br />
<br />

A simple way to think about it:
- CNI part: connects pods to the cluster network
- Policy part: controls which traffic is allowed or denied
- Operations part: supports different networking approaches for different environments

That combination is one reason Calico is commonly used in on-prem, cloud, and edge Kubernetes clusters.

## How Calico works inside a cluster

Calico installs several components that work together. The most important beginner-level pieces are:
- CNI plugin: attaches pods to the network
- IPAM plugin: assigns pod IP addresses
- Felix: programs routing, filtering, and policy rules on each node
- kube-controllers: sync cluster state
- Typha: helps scale large deployments
- BIRD: used in BGP-based routing setups

You do not need to memorize every component at first. The main idea is that Calico runs logic on each node so networking and policy are enforced close to the workloads.<br />
<br />

A practical example:<br />
<br />

If a frontend pod on node A needs to talk to a backend pod on node B, Calico helps route that traffic and can also check whether a policy allows it.

## Networking modes: routed, overlay, and eBPF

One of Calico’s strengths is flexibility. It can work in different networking modes depending on your environment.<br />
<br />

**Routed networking with BGP**<br />
In routed mode, Calico can use BGP to advertise routes between nodes. This is a strong fit when your infrastructure team controls the network and wants efficient routing without extra encapsulation overhead.<br />
<br />

**Overlay networking with VXLAN or IP-in-IP**<br />
In environments where the underlay network cannot easily route pod IPs, Calico supports encapsulation. This is common in cloud or constrained environments. Overlay mode is often easier to get working, but it can add overhead compared with pure routed networking.<br />
<br />

**eBPF dataplane**
Calico also supports an eBPF dataplane. At a high level, eBPF lets Calico handle networking logic efficiently in the Linux kernel. This can improve performance and enable advanced behavior, but it is usually something to adopt after you already understand the basics.<br />
<br />

A good beginner rule:
- Use overlay when you want simpler cross-node connectivity
- Use BGP/routed mode when you want more direct routing and your network supports it
- Explore eBPF when you want advanced performance or platform-level tuning

## Network policy: Calico’s biggest practical advantage

For many teams, the real reason to choose Calico is network policy. Kubernetes has native `NetworkPolicy`, but Calico adds richer policy features such as broader matching options, explicit deny behavior, ordering, and policy that can apply beyond just pods.<br />
<br />

Here is a simple Kubernetes `NetworkPolicy` example that allows only frontend pods to reach backend pods on port 8080:
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
      ports:
        - protocol: TCP
          port: 8080
```

This policy selects pods labeled `app: backend` and allows incoming traffic only from pods labeled `app: frontend` on TCP port `8080`.<br />
<br />

Calico can enforce standard Kubernetes policies like this, but it also has its own richer policy model. That becomes useful when platform or security teams want tighter control than native Kubernetes policy alone provides.

## Common mistakes and anti-patterns

A frequent mistake is installing Calico and then never writing any network policies. In that case, you are using it mostly as a network plugin and missing one of its biggest benefits: segmentation.<br />
<br />

Another common mistake is choosing a mode without understanding the environment:
- Picking BGP without knowing whether the network team supports route exchange
- Picking overlay mode everywhere, even where routed networking would be simpler and faster
- Turning on advanced features like eBPF too early without understanding debugging and compatibility implications

A third anti-pattern is writing overly broad policies, such as allowing traffic from everywhere just to “make it work.” That usually leads back to a flat, insecure cluster design.<br />
<br />

A better approach is:
- Start with basic connectivity
- Add simple namespace or app-based policies
- Tighten rules gradually

Move to advanced dataplanes only when there is a clear reason<br />
<br />

This staged approach is easier to operate and troubleshoot.

## When Calico is a strong choice

Calico is a strong fit when you want one solution for both Kubernetes networking and security policy. It is especially useful for teams that care about zero-trust style communication between workloads, need flexibility across cloud and on-prem environments, or want room to grow into more advanced routing and dataplane options later.<br />
<br />

A simple real-world example:
- A small team may use Calico first just for pod networking
- As the platform grows, they add policies between frontend, backend, and database workloads
- Later, they may tune routing or adopt eBPF for better scale or performance

That makes Calico useful not only for day-one setup, but also for long-term platform maturity.
