# Exam-ready labs

A full lab exam draws 15 to 20 labs from the training repositories
(`astrona-io/ATS*`) and runs them on a few kind clusters that the student's
machine builds before the clock starts. Several labs share one cluster, and a
lab no longer gets a cluster named after itself. A lab written for lab mode
only breaks there in four ways:

- it uses the same namespace as other labs (`starfleet`), so two labs on one
  cluster overwrite each other;
- its scripts refuse to run unless the context is `kind-astro-<lab>`, or they
  hardcode node container names and `podman`;
- it has one validation script, so a student who fixes four of five findings
  gets nothing;
- the exam cannot tell how long the task takes.

This guide is the convention that fixes those.

## ATS020 is the model

ATS020 (CNPE: Observability and Operations) is the training format to follow.
Where an older repository differs from ATS020 on lab layout, manifest fields,
check style or the question text, do it the ATS020 way. ATS020 already has
most of what an exam needs:

- one grader per outcome, `validation/validate-<outcome>.sh`, listed in
  `validation.scripts` with a `name` and a `description`;
- graders print one `PASS:` or `FAIL:` line and exit 0 or 1;
- `testing/verify-start.sh` runs first in `testing.init` and proves that
  every outcome fails on the starting state, then the reference solution runs,
  and `astrona test` checks that every outcome passes;
- the time is a sentence under the question title:
  `Allow 10–15 minutes for the tasks.`

Three things ATS020 does not have, and this guide adds: a namespace per lab
(ATS020 shares `starfleet` and `outpost` between labs), node container names
from the environment (ATS020 never execs into a node), and a context guard
that refuses to run against any cluster but the lab's own.

ATS031 (Cluster Setup) applies the convention to the CKS labs:
`sections/section-020/module-05/labs/lab-02` is a short one to copy from.
ATS031 still keeps its own docs keys (`examQuestion`, `caseStudy`, `guide`),
its `docs/` folder and its question front matter; those do not affect the
exam and are left for a separate change.

## The rules

### 1. Each lab has its own namespaces

Name every namespace the lab creates `<role>-<training>-<section>-<module>-<lab>`,
taken from the lab's `metadata.name` (`ats-031-lab-020-05-02`):

| Before | After |
| --- | --- |
| `starfleet` | `starfleet-031-020-05-02` |
| `outpost` | `outpost-031-020-05-02` |
| `dock` | `dock-031-020-05-02` |

The name is unique across every training, so the draw can put any two
namespace-scoped labs on the same cluster. Rename the namespace everywhere it
appears: bootstrap manifests and scripts, the solution, the graders, the
`kubernetes.io/metadata.name` values in NetworkPolicy selectors, etcd keys
such as `/registry/secrets/<namespace>/...`, `question.md`, `solution.md`,
`docs/` and the README. Story text that names a team ("the starfleet team")
can stay as it is; text that names the namespace uses the new name in
backticks.

Shared namespaces the lab only reads (`kube-system`, `default`) keep their
names. A lab that writes to one of them, or to anything cluster-wide (nodes,
static pod manifests, the kubelet, admission, CRDs, ClusterRoles), is
`examScope: cluster` (rule 5).

### 2. The context guard and node names come from the environment

Every script and check refuses to run unless `kubectl config current-context`
is the lab's own context. That guard stays: CKS setups restart kubelets, edit
static pods and write node files, and must never land on another cluster. It
reads the expected context from the environment, so it also passes on an exam
cluster. astrona sets three variables for every kind lab script and `command`
check:

| Variable | Lab mode value |
| --- | --- |
| `ASTRONA_KUBE_CONTEXT` | `kind-astro-<lab>`; the context in `KUBECONFIG` |
| `ASTRONA_KIND_CLUSTER` | `astro-<lab>`; nodes are `$ASTRONA_KIND_CLUSTER-control-plane` and `-worker` |
| `ASTRONA_CONTAINER_ENGINE` | `docker` or `podman` |

Read them with the lab mode value as the fallback, so the lab also runs with
an older `astrona`:

```bash
#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-05-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-05-02}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
```

and run `"$engine" exec "$worker_name" ...`, never `podman exec
astro-ats-031-lab-020-05-02-worker ...`. Python checks use `NODE`, `WORKER`,
`ENGINE` and `node_exec()` from the shared `testing/check.py`. Static pod
names follow the node: `'kube-apiserver-' + NODE`, not
`kube-apiserver-astro-ats-031-lab-020-05-02-control-plane`. Python helpers
guard the same way: `CONTEXT = os.environ.get('ASTRONA_KUBE_CONTEXT') or
'kind-astro-<lab>'`, then exit unless the current context matches. Never drop
the guard to make a lab portable; make it read `ASTRONA_KUBE_CONTEXT`
instead. A lab that never touches a node needs only the context variable.

`question.md`, `solution.md` and the prerequisites keep the lab mode block
(`export KUBECONFIG="$(astrona kubeconfig <lab>)"` and the two node names):
that is what a student types in lab mode. The exam shows its own header with
the context and node names.

### 3. One grader per outcome, with points

Split the grade into the outcomes the task asks for, one grader each, as
ATS020 does. A student who gets three of five right earns three outcomes'
points.

- An outcome is something the task asks the student to change: a file mode,
  a flag, a policy that allows one path. Name it in kebab-case after what it
  checks (`kubelet-file-modes`, `tls-min-version`).
- Every outcome fails on the starting state. A check that already passes at
  the start (the app still answers, the node is still Ready) is a *guard*,
  not an outcome: it runs with every outcome and earns nothing alone. A
  solution that breaks the node fails every outcome.
- Every outcome passes for the reference solution. Splitting never changes
  pass or fail for a correct answer.
- Points: 1 for a single change, 2 for an outcome that takes clearly more
  work (two files, a restart and a wait). Most outcomes are 1.
- A failing grader names what is missing in its `FAIL:` line ("Set mode 600
  on kubelet.conf", "Missing configmap review in namespace
  starfleet-031-050-01-01"), not a stack trace.

The graders are `validation/validate-<outcome>.sh`, as in ATS020. A lab can
write each one as plain bash, the ATS020 way, with a bounded retry where the
state takes time to settle:

```bash
#!/usr/bin/env bash
set -euo pipefail
for _ in $(seq 1 24); do
  if [ "$(kubectl -n starfleet-031-010-01-01 get networkpolicy default-deny -o name 2>/dev/null)" ]; then
    echo "PASS: default-deny exists"; exit 0
  fi
  sleep 5
done
echo "FAIL: Create NetworkPolicy default-deny in starfleet-031-010-01-01"
exit 1
```

The CKS labs in ATS031 share one Python grader instead, because their checks
compare resource contracts and node files. There each
`validation/validate-<outcome>.sh` is the same three-line wrapper that runs
`validate.sh <outcome>`, which runs `testing/check.py <outcome>`:

- `testing/check.py` is the same file in every lab; copy it from ATS031 and do
  not edit it per lab. It prints `PASS: <outcome>` or `FAIL: <reason>`.
- `testing/requirements.json` holds `context`, `cluster` and `namespace` (the
  lab mode context and cluster name, and the main namespace); `check.py`
  checks the context first, plus `resources` and `behavior`
  entries. An entry with `"outcome": "<id>"` belongs to that outcome; one
  without is a guard.
- `testing/live.py` holds the checks that need code. Guards are plain
  statements; each outcome's checks sit under `if wants('<id>'):`.
- `check.py` fails an outcome id that no entry or `wants()` block uses, so a
  typo in `config.yaml` cannot pass silently.

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

After, one grader per outcome:

```yaml
validation:
  scripts:
  - name: kubelet-file-modes
    description: kubelet config.yaml and kubelet.conf have mode 600
    type: file
    source: validation/validate-kubelet-file-modes.sh
    points: 2
  - name: certificate-rotation
    description: The kubelet rotates its certificates
    type: file
    source: validation/validate-certificate-rotation.sh
    points: 1
  - name: tls-min-version
    description: The kubelet accepts TLS 1.2 or later only
    type: file
    source: validation/validate-tls-min-version.sh
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

### 4. `astrona test` proves it, as in ATS020

`testing.init` runs three steps:

```yaml
testing:
  init:
  - name: verify-start
    description: Verify the starting state and reject the unfinished lab
    type: file
    source: testing/verify-start.sh
  - name: reference-result
    type: file
    source: solution/apply.sh
  - name: wait-solved
    description: Wait until the reference solution settles and every outcome passes
    type: file
    source: testing/wait-solved.sh
```

- `testing/verify-start.sh` runs every `validation/validate-*.sh` and fails
  unless each one exits nonzero with a `FAIL:` line. It prints each outcome's
  reason, so the log shows what a student sees on an untouched lab.
- `solution/apply.sh` applies the reference solution.
- `testing/wait-solved.sh` retries the whole grade for up to two minutes, so a
  restarted kubelet or API server has answered before astrona runs the
  graders. ATS020's graders retry on their own and do not need this step; the
  ATS031 graders check once.

`astrona test <lab-dir> --accept-terms --headless` then builds a fresh
cluster, runs the steps and every grader, and must report every outcome
passed. Copy `verify-start.sh` and `wait-solved.sh` from ATS031; they are the
same in every lab.

### 5. The time line

Under the title of `question.md`, the ATS020 sentence:

```markdown
# Remediate Five Kubelet Benchmark Findings

Allow about 12 minutes for the tasks.
```

A range (`Allow 10–15 minutes for the tasks.`) is fine; the content sync
takes the upper bound as the lab's exam time. It is how long a prepared
student needs in the exam, reading included, not the lab mode
`estimated_duration` (which covers learning). Be honest: count the commands
in `solution.md`, add the waits (a kubelet or API server restart is one to two
minutes), and round up. A lab over 20 minutes cannot join an exam; split the
task or leave it out.

### 6. `examScope` in `astrona.yaml`

Set it on the lab's entry once the lab follows rules 1 to 5 and its
`runtime.kind` fits the exam's `lab_exam.clusters` profile (same node counts
and CNI, addons a subset; `image`, `preloadImages` and `dns` are not
compared):

- `examScope: namespace`: everything the lab creates or changes is inside its
  own namespaces. It may read cluster-wide state.
- `examScope: cluster`: the lab changes something outside its namespaces
  (nodes, static pods, the kubelet, API server flags, admission, cluster-wide
  RBAC or CRDs, `kube-system`). It gets a cluster to itself in the draw.
  A pod on the node's network with a fixed port is `cluster` too: the port
  can clash with another lab, or with the CNI's own ports.
- Two `cluster` labs never share a cluster, so they may use the same node
  paths; namespace labs must not write to a node at all.

When unsure, choose `cluster`. Leave `examScope` off a lab that does not fit
the profile; the content sync reports such a lab as unable to join.

The CKS profile is one control plane and one worker on kindnet (no `cni`
addon), see `exams/kubestronaut/cks.yaml`. A CKS lab that needs Calico or
Cilium for NetworkPolicy does not fit it.

Two more traps the ATS031 conversion found:

- An image pinned by digest must not be in `preloadImages`: a preloaded image
  has no registry digest in the pod status, so the pinned rollout never
  finishes.
- Pin downloaded tools to a version (`cosign v2.4.1`, not
  `releases/latest`); a new major release can break the setup.

## Checklist

For each lab:

- [ ] Namespaces renamed to `<role>-<training>-<section>-<module>-<lab>` in
      every file; `grep -rnw starfleet` finds nothing left.
- [ ] Every script and helper keeps its context guard, reading
      `ASTRONA_KUBE_CONTEXT` with the lab mode context as fallback.
- [ ] Scripts that exec into a node read `ASTRONA_KIND_CLUSTER` and
      `ASTRONA_CONTAINER_ENGINE` with fallbacks; nothing names
      `astro-<lab>-...` or `podman` directly.
- [ ] `config.yaml` lists one `validation.scripts` entry per outcome, each
      with `description`, `points` and `source:
      validation/validate-<outcome>.sh`, and no `validation.script`.
- [ ] Every grader prints one `PASS:` or `FAIL:` line; a `FAIL:` names what
      is missing.
- [ ] ATS031-style labs: `testing/check.py`, `testing/verify-start.sh`,
      `testing/wait-solved.sh` and `validation/*.sh` are byte-identical to
      ATS031's; `requirements.json` has `context`, `cluster` and `namespace`.
- [ ] `testing.init` runs `verify-start`, the reference solution, then
      `wait-solved`.
- [ ] `question.md` has `Allow about N minutes for the tasks.` under the
      title, N at most 20 for the exam.
- [ ] `examScope` set in `astrona.yaml` when the lab fits the profile.
- [ ] `astrona validate <lab-dir>` passes, and `astrona test <lab-dir>
      --accept-terms --headless` passes: every outcome fails at the start and
      passes after the solution.
- [ ] Do not touch `task_kind`, `tags` or `topic`: other tooling owns them.
