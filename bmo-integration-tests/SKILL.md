---
name: bmo-integration-tests
description: >-
  Adds or extends service integration tests against real databases, API/RPC
  transports, and message brokers using the smallest real stack that proves the
  production boundary. Use when the user asks for integration tests, real-DB or
  Testcontainers coverage, HTTP/gRPC/RPC handler wiring tests, or queue/event
  producer and consumer verification.
---

# Integration tests (real DB + transport + broker)

## Goal

Prove behavior through **real infrastructure** (database, HTTP/gRPC/RPC transport, message broker, cache) and **real in-process wiring**. Stub **only external boundaries** the service does not own (third-party APIs, payment/custody providers, external microservices).

Handler or service tests that mock the database, ORM, broker client, or transport layer are unit tests, not integration tests.

Pair with [`bmo-step-deliver`](../bmo-step-deliver/SKILL.md) for multi-file work: harness → seeds → spec(s) as separate units.

---

## Workflow (follow in order)

### 1. Discover the repo's test environment

Inspect the repository before designing any harness:

1. Check package/build manifests (`package.json`, `Makefile`, `pyproject.toml`, `go.mod`, `Cargo.toml`), CI workflows, and `.env.example` / `docker-compose*` to see how databases, brokers, and test runners run locally and in CI.
2. Search existing `integration` / `e2e` suites for reusable harness factories, template-DB / Testcontainers setup, migration hooks, seed builders, and polling helpers.

**Done:** Existing runner command, infrastructure provisioning mechanism, and reusable harness helpers (or their absence) are recorded from the repo.

### 2. Map the production boundary

Read the real production entrypoint and contract/schema definitions once (never guess wire shapes):

| Question | Why it matters |
|----------|----------------|
| **Ingress?** HTTP route, gRPC/RPC method, queue/stream consumer, job | Determines how the test triggers the flow |
| **Required real infra?** DB only, DB + transport, DB + broker/cache | Selects the smallest harness tier |
| **Assertion seam?** Persisted rows, response payload/status, outbound publish, queue drain/fan-out | Selects what the test asserts |
| **Async fan-out?** Fire-and-forget events or background consumers | Requires bounded condition polling before assertions |

**Done:** Entrypoint, contract types, required real infra, and assertion seam are named.

### 3. Pick the smallest real tier

Boot only the infrastructure required to prove the target boundary:

| Tier | Real | Stubbed / omitted | Use when |
|------|------|-------------------|----------|
| **DB + domain/service** | Database + migrations + repositories + services | External APIs, transport server, broker | Persistence, SQL/ORM queries, transactions, constraints |
| **DB + API/RPC transport** | Above + real HTTP/gRPC/RPC server & typed client | External APIs, unneeded background workers | Wire serialization, validation, auth middleware, status/error mapping + DB |
| **DB + broker producer** | Above + real publisher pipeline + spy/capture at last in-process broker boundary (or ephemeral exchange) | External APIs, downstream consumer services | Outbound event/message contract without booting downstream services |
| **DB + broker consumer** | Real DB + real broker + consumer worker loop | Unneeded HTTP server, external APIs | Inbound message → state transition → ack/retry/DLQ/outbound fan-out |

Keep the default harness minimal; add opt-in transport-aware or broker-aware factory variants rather than booting the entire application for every test. When building a new harness or broker seam from scratch, read [reference.md](reference.md).

**Done:** One tier is selected and justified against the boundary from Step 2.

### 4. Isolate parallel resources

Every suite claims collision-free resources so parallel test workers never fight over state or ports:

- **Database:** dedicated cloned template DB, per-suite schema, per-worker container, or per-test rolled-back transaction (only when the code under test shares that single connection).
- **Network port:** OS-assigned ephemeral port (`0`) or a registered suite-unique port.
- **Broker / cache:** unique vHost, topic/queue prefix, consumer group, or key namespace per suite.

Standard lifecycle:

```text
beforeAll  → provision isolated DB/vhost/port, run migrations, start harness
beforeEach → clear call history, re-apply default stub return values, reset tables in FK order, seed scenario
afterAll   → stop consumers/servers/clients cleanly, drop ephemeral DB/vhost/containers
```

**Done:** Suite setup and teardown leave zero shared port, database, or queue collisions across parallel runs.

### 5. Seed realistic state

| Data | Approach |
|------|----------|
| Reference / parent entities | Parameterized SQL or shared factory builders with realistic IDs (valid UUIDs, real enum values, valid timestamps) |
| Domain invariants (balances, state machines, ledgers) | Seed through the real write service or repository when downstream logic depends on its invariants |
| Multi-tenant / cross-actor cases | Named scenario helper documenting which actor owns which records |

**Done:** Seeds use contract-valid types and reset cleanly between tests.

### 6. Trigger production ingress and assert the seam

1. **Trigger** through the same ingress production callers use: generated RPC/HTTP client, bound route/handler factory, or real broker publish.
2. **Assert** the specific seam(s) under test:
   - **Transport/handler result:** status code, typed response payload, error code.
   - **Database state:** persisted rows, state transitions, absence of partial writes on rollback.
   - **Broker producer:** spy or capture at the **last in-process client boundary** before bytes leave the service, using a named lookup helper instead of raw call-index subscripts.
   - **Broker consumer:** wait for consumer readiness → publish message → wait for queue drain / condition → assert DB state and any outbound fan-out on a **separate probe channel** (never read probes from the busy worker channel).
3. **Async side effects:** poll with a bounded `waitUntil(predicate, { timeoutMs, intervalMs })` helper rather than fixed `sleep` timers or synchronous post-return checks.

**Done:** Every assertion targets a real boundary seam with typed contract expectations and deterministic async synchronization.

### 7. Verify

Run the targeted integration file serially first via the repo's runner (e.g. `--runInBand`, `-p 1`, `--maxWorkers=1`, or single-file invocation), then confirm teardown exits cleanly without open handles. If required containers/services cannot run in the current environment, state what blocked execution and provide exact commands to start infra and run the spec.

**Done:** Targeted integration suite exits `0` against real infrastructure (or exact environment blocker + runnable commands are reported).

---

## Design rules

1. **Smallest real stack** — boot full app wiring only when testing startup or end-to-end broker consumption.
2. **One seam per test** — separate DB persistence edge cases from broker wire-contract assertions when practical.
3. **Strict contract types** — type fixtures, RPC payloads, and captured broker messages with the real schema types (never `any`).
4. **Re-apply stub defaults after clearing mocks** — `clearAllMocks` / `resetMocks` can strip default return values needed by later tests.
5. **Test cross-service contracts at each service's boundary** — assert the producer contract in service A and the consumer contract in service B against the shared schema rather than booting multiple services in one test process.

## Disclosed blueprints

For harness factory patterns, template-DB/Testcontainers isolation, bounded `waitUntil` + broker producer/consumer skeletons, and bootstrapping a repo with no existing harness, read [reference.md](reference.md).
