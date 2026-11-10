# Exam-ready labs

A full lab exam draws 15 to 20 labs from the training repositories
(`astrona-io/ATS*`) and runs them on a few kind clusters that the student's
machine builds before the clock starts. Several labs share one cluster, and a
lab no longer gets a cluster named after itself. A lab written for lab mode
only breaks there in four ways:

- it uses the same namespace as other labs (`starfleet`), so two labs on one
  cluster overwrite each other;
- its scripts refuse to run unless the context is `kind-astro-<lab>`, and they
  hardcode node container names and `podman`;
- it has one validation script, so a student who fixes four of five findings
  gets nothing;
- the exam cannot tell how long the task takes.

This guide is the convention that fixes those. ATS031 (Cluster Setup) is the
reference: every lab under `sections/` in that repository follows it, and
`sections/section-020/module-05/labs/lab-02` is a short one to copy from.

## The rules

### 1. Each lab has its own namespaces

Name every namespace the lab creates `<role>-<training>-<section>-<module>-<lab>`,
taken from the lab's `metadata.name` (`ats-031-lab-020-05-02`):

| Before | After |
| --- | --- |
| `starfleet` | `starfleet-031-020-05-02` |
| `outpost` | `outpost-031-020-05-02` |
| `dock` | `dock-031-020-05-02` |

The name is unique across every CKS training, so the draw can put any two
namespace-scoped labs on the same cluster. Rename the namespace everywhere it
appears: `bootstrap/` manifests and scripts, `solution/`, `testing/`, the
`kubernetes.io/metadata.name` values in NetworkPolicy selectors, etcd keys
such as `/registry/secrets/<namespace>/...`, `question.md`, `solution.md`,
`docs/` and the README. Story text that names a team ("the starfleet team")
can stay as it is; text that names the namespace uses the new name in
backticks.

Shared namespaces the lab only reads (`kube-system`, `default`) keep their
names. A lab that writes to one of them, or to anything cluster-wide (nodes,
static pod manifests, the kubelet, admission, CRDs, ClusterRoles), is
`examScope: cluster` (rule 5).

### 2. Scripts find the cluster from the environment

`astrona` gives every kind lab script and `command` check three variables:

| Variable | Lab mode value |
| --- | --- |
| `ASTRONA_KUBE_CONTEXT` | `kind-astro-<lab>` |
| `ASTRONA_KIND_CLUSTER` | `astro-<lab>`; nodes are `$ASTRONA_KIND_CLUSTER-control-plane` and `-worker` |
| `ASTRONA_CONTAINER_ENGINE` | `docker` or `podman` |

On an exam cluster they point at that cluster instead. Read them with the lab
mode value as the fallback, so the lab also runs with an older `astrona`.
Every shell script (`validate.sh`, `bootstrap/setup.sh`, `solution/apply.sh`,
`testing/smoke.sh`) starts like this:

```bash
#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-05-02}"
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-05-02}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
```

and runs `"$engine" exec "$worker_name" ...`, never `podman exec
astro-ats-031-lab-020-05-02-worker ...`. Python checks use `NODE`, `WORKER`,
`ENGINE` and `node_exec()` from the shared `testing/check.py`. Static pod
names follow the node: `'kube-apiserver-' + NODE`, not
`kube-apiserver-astro-ats-031-lab-020-05-02-control-plane`.

`question.md`, `solution.md` and `docs/prerequisites.md` keep the lab mode
block (`export KUBECONFIG="$(astrona kubeconfig <lab>)"` and the two node
names): that is what a student types in lab mode. The exam shows its own
header with the context and node names.

### 3. One validation script per outcome, with points

Split the grade into the outcomes the task asks for, one validation script
each. A student who gets three of five right earns three outcomes' points.

- An outcome is something the task asks the student to change: a file mode,
  a flag, a policy that allows one path. Name it in kebab-case after what it
  checks (`kubelet-file-modes`, `tls-min-version`).
- Every outcome fails on the unsolved lab. A check that already passes at the
  start (the app still answers, the node is still Ready) is a *guard*, not an
  outcome: it runs with every outcome and earns nothing alone. A solution that
  breaks the node fails every outcome, as before.
- Every outcome passes for the reference solution. Splitting never changes
  pass or fail for a correct answer.
- Points: 1 for a single change, 2 for an outcome that takes clearly more
  work (two files, a restart and a wait). Most outcomes are 1.

How it is wired in the ATS repositories:

- `testing/check.py` is the same file in every lab. `python3 testing/check.py`
  grades the whole lab; `python3 testing/check.py <outcome>` grades one.
  Copy it from ATS031, do not edit it per lab.
- `testing/requirements.json` holds `context`, `cluster` and `namespace` (the
  lab mode values and the main namespace), plus `resources` and `behavior`
  entries. An entry with `"outcome": "<id>"` belongs to that outcome; one
  without is a guard.
- `testing/live.py` holds the checks that need code. Guards are plain
  statements; each outcome's checks sit under `if wants('<id>'):`.
- `testing/outcomes/<id>.sh` is a three-line wrapper, the same in every lab,
  that runs `validate.sh <id>`. Its file name is the outcome id.
- `validate.sh` passes its arguments on to `check.py`.

Before, one script graded everything:

```yaml
validation:
  script:
    name: verify-fields-and-live-evidence
    type: file
    source: validate.sh
```

```python
# testing/live.py
cfg = configz()
assert node_ready(WORKER), 'The worker node must stay Ready'
assert mode('/var/lib/kubelet/config.yaml') == '600', 'Set mode 600 on config.yaml'
assert mode('/etc/kubernetes/kubelet.conf') == '600', 'Set mode 600 on kubelet.conf'
assert cfg.get('rotateCertificates') is True, 'Enable kubelet certificate rotation'
assert cfg.get('tlsMinVersion') == 'VersionTLS12', 'Set tlsMinVersion to VersionTLS12'
```

After, one script per outcome:

```yaml
validation:
  scripts:
  - name: kubelet-file-modes
    description: kubelet config.yaml and kubelet.conf have mode 600
    type: file
    source: testing/outcomes/kubelet-file-modes.sh
    points: 2
  - name: certificate-rotation
    description: The kubelet rotates its certificates
    type: file
    source: testing/outcomes/certificate-rotation.sh
    points: 1
  - name: tls-min-version
    description: The kubelet accepts TLS 1.2 or later only
    type: file
    source: testing/outcomes/tls-min-version.sh
    points: 1
```

```python
# testing/live.py
cfg = configz()
assert node_ready(WORKER), 'The worker node must stay Ready'   # guard
if wants('kubelet-file-modes'):
    assert mode('/var/lib/kubelet/config.yaml') == '600', 'Set mode 600 on config.yaml'
    assert mode('/etc/kubernetes/kubelet.conf') == '600', 'Set mode 600 on kubelet.conf'
if wants('certificate-rotation'):
    assert cfg.get('rotateCertificates') is True, 'Enable kubelet certificate rotation'
if wants('tls-min-version'):
    assert cfg.get('tlsMinVersion') == 'VersionTLS12', 'Set tlsMinVersion to VersionTLS12'
```

`check.py` fails an outcome id that no entry or `wants()` block uses, so a
typo in `config.yaml` cannot pass silently.

### 4. A Time line in the task

Put a `**Time:**` line under the title of `question.md`:

```markdown
# Remediate Five Kubelet Benchmark Findings

**Time:** about 12 min
```

It is how long a prepared student needs in the exam, reading included, not
the lab mode `estimated_duration` (which covers learning). Be honest: count
the commands in `solution.md`, add the waits (a kubelet or API server restart
is one to two minutes), and round up. A lab over 20 minutes cannot join an
exam; split the task or leave it out.

### 5. `examScope` in `astrona.yaml`

Set it on the lab's entry once the lab follows rules 1 to 4 and its
`runtime.kind` fits the exam's `lab_exam.clusters.kind` profile (same node
counts and CNI, addons a subset; `image`, `preloadImages` and `dns` are not
compared):

- `examScope: namespace`: everything the lab creates or changes is inside its
  own namespaces. It may read cluster-wide state.
- `examScope: cluster`: the lab changes something outside its namespaces
  (nodes, static pods, the kubelet, API server flags, admission, cluster-wide
  RBAC or CRDs, `kube-system`). It gets a cluster to itself in the draw.

When unsure, choose `cluster`. Leave `examScope` off a lab that does not fit
the profile; the content sync reports such a lab as unable to join.

The CKS profile is one control plane and one worker on kindnet (no `cni`
addon), see `exams/kubestronaut/cks.yaml`.

## Checklist

For each lab:

- [ ] Namespaces renamed to `<role>-<training>-<section>-<module>-<lab>` in
      every file; `grep -rnw starfleet` finds nothing left.
- [ ] Every `.sh` reads `ASTRONA_KUBE_CONTEXT`, `ASTRONA_KIND_CLUSTER` and
      `ASTRONA_CONTAINER_ENGINE` with fallbacks; no script or `live.py`
      names `astro-<lab>-...` or `podman` directly.
- [ ] `testing/check.py` and `testing/outcomes/*.sh` are byte-identical to
      ATS031's.
- [ ] `requirements.json` has `context`, `cluster` and `namespace`.
- [ ] `config.yaml` lists one `validation.scripts` entry per outcome, each
      with `description` and `points`, and no `validation.script`.
- [ ] `question.md` has `**Time:** about N min`, N at most 20 for the exam.
- [ ] `examScope` set in `astrona.yaml` when the lab fits the profile.
- [ ] Run it end to end with `astrona`: `astrona run <lab-dir> --headless
      --accept-terms --local-only`; `astrona submit <lab> --keep -o json`
      fails **every** outcome; `solution/apply.sh` applied; `astrona submit
      <lab>` passes every outcome.
- [ ] Do not touch `task_kind`, `tags` or `topic`: other tooling owns them.
