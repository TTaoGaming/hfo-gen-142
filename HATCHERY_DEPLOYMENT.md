# Portable Hatchery implementation and measured scope

Observed 2026-09-14 UTC. This is a bootstrap deployment plus finite scientific
assay, not admission of a general unattended swarm. Fleet evolutionary WIP stays
one. No provider caps, existing schedulers or runner registrations were changed.

## Three-host bootstrap

The same `hatchery/adapter.py` release was installed on the Windows laptop,
Oracle Linux ARM64 and OVH Linux x86_64. SHA-256:
`88fc48694ea55881e04608a9a9e8626647a69fe1ca31315a10af6150e674c0f6`.
All three returned the same canonical fixture output, SHA-256
`ee2538a35bfe57e6c4a830e5ff00382345e972fcb3d90a88214bbb63745134fa`.

VPS execution used existing systemd transient services under the dedicated
non-sudo service user: 15 seconds, 128 MiB, one CPU, 16 tasks, private network,
read-only system and no privilege escalation. Laptop execution used a bounded
Python child; Windows Job Object resource enforcement is not yet demonstrated.
The adapter advertises only `bootstrap.reduce.v1`. It deliberately does not
advertise provider inference, arbitrary code, external sending or an autonomous
loop. Deployment does not turn these descriptors into ADMITTED hosts.

## Existing Cloudflare owner: finite caller replacement

`hatchery/native-assay.mjs` was added to the existing actor Worker. It reuses
the existing Durable Object, R2 and NativeJob Workflow service binding. A fixed,
authenticated assay route expires at 2026-09-14T03:00:00Z; it adds no cron,
namespace, provider call or general-purpose command executor.

Caller A started `gen142-hatchery-g1-20260914-r1` and exited. A fresh caller B
read checkpoint 1, submitted the installed adapter result and observed native
Workflow `complete` / output `completed`. The persisted fixed-oracle ACK binds
the output hash above. Accepted event count was one; duplicate submission returned
the existing state and conflicting content was rejected. Offline tests also
retain an ambiguous event send without redispatch.

This proves the narrow caller-replacement fixture. It does not prove machine
crash recovery, stale lease fencing, shared provider-account races or independent
model review. The fixed oracle and tests have the same author as this bridge.

## Two sequential packing generations

`hatchery/packing_generations.py` invokes an existing SciPy refinement kernel as
a finite workload, rather than adding another search scheduler. Oracle completed
two generations in one network-isolated native service: 240-second limit,
512 MiB, one CPU, 32 tasks, zero provider calls and zero retries. Measured service
runtime was 6.570 seconds. Every generation consumed the previous accepted bytes.

Input and final champion SHA-256:
`8ed8148be615d06c4bf37bf8fe5715248923486b93ab36d2d49b3d503b9da517`.
Both generations retained radius **0.3099639332166260**; neither improved it.
Each evaluated 13 configurations (normalization plus 12 minimax variants).
The frozen evaluator uses rational arithmetic to check all 119 containment and
7,021 pair constraints. Malformed dimension/count, duplicate center and oversized
radius controls reject. The spherical-code donor remains credited to Henry Cohn.

Synthetic control tests are not independent human acceptance. These two finite
CPU generations are not an LLM-driven MOME search, not proof of restart during
evolution, and not the full Gen142 G3 autonomy gate. Packing was launched through
the native supervisor, not the bootstrap reduction profile or a cloud scheduler.
The public `hatchery/packing-fixture` binds the source, evaluator and input;
sanitized receipts preserve both generations. No keeper email was sent.

## Remaining adoption work

Connect a bounded packing workload to the admitted native host lifecycle and
prove interruption/recovery, disk enforcement, independent evaluation and
stale-fence rejection before unattended operation. Provider adapters also need
atomic shared-account reservations and settlement across hosts. Ollama is an
optional adapter to that same contract; its installation is not host admission.
Research and application preparation profiles are specified in
[workload profiles](WORKLOAD_PROFILES.md); their executors are not yet implemented.

## Verification

Run `python contracts/check_contract.py`,
`python -m unittest discover -s hatchery -p "test_*.py"`, and
`node hatchery/native-assay.test.mjs`.

For the scientific fixture, use an isolated directory containing copies of
`packing-fixture/*` and `packing_generations.py`, with NumPy and SciPy installed.
Run the driver under a native resource-limited supervisor. Generation directories
use exclusive creation; a repeated launch refuses rather than overwrites evidence.

## Strife and guards

- Bootstrap installation was previously easy to confuse with full host admission:
  descriptors retain UNADMITTED and enumerate unsupported capabilities.
- Payload-hash deduplication alone could admit conflicting terminal results:
  the finite bridge reserves one immutable work slot before sending an event.
- A successful process could conceal no scientific improvement: each generation
  reports RETAINED or IMPROVED and preserves exact parent/result hashes.
- Sandbox child-process spawning prevented `node --test`: direct execution of
  the node:test module passed without changing the tests or weakening assertions.
