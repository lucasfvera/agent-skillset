---
name: bmo-integration-tests
description: >-
  Add or extend integration tests with real Postgres, RabbitMQ, and gRPC in
  Roxom services (roxtarsverse apps like tx, hermod, and similar repos). Use
  when the user asks for integration tests, end-to-end service tests, real-DB
  tests, Rabbit publish/consumer verification, or gRPC handler integration
  coverage. Prefer the smallest real stack that proves the behavior boundary.
---

# Integration tests (real DB + Rabbit + gRPC)

## Goal

Prove behavior through **real infrastructure** (Postgres, RabbitMQ, gRPC) and **real in-process service/handler wiring**. Mock only **external systems** the service does not own (Fireblocks, Pricetrox, third-party APIs, etc.).

**Not integration:** handler-only tests with mocked `pg`/`rabbitmq`/`grpc` (tx `jest.config.grpc-handlers.ts`, hermod `tests/unit/`).

## When to use

- User wants confidence a flow works end-to-end (handler → service → DB → side effect).
- User wants to assert Rabbit publishes or queue consumption.
- User wants gRPC server + generated client against real DB state.
- User references tx internal-transfer notification tests or hermod notification suites as the pattern.

Pair with **`/bmo-step-deliver`** for multi-file work: harness → seeds → spec(s) as separate units.

---

## Workflow (follow in order)

### 1. Discover the production boundary

Before writing code, answer:

| Question | Why |
|----------|-----|
| **Ingress?** RPC handler, gRPC, HTTP, Rabbit consumer, job | Determines how the test triggers the flow |
| **Success path needs what infra?** DB only, DB+gRPC, DB+Rabbit | Picks harness tier |
| **Side effect to prove?** DB rows, Hermod publish, topic fan-out, gRPC response | Picks assertion seam |
| **Async fan-out?** fire-and-forget notifications | Needs `waitUntil` before Rabbit/DB assertions |

Read the real handler/service once. Do not guess message shapes — use `@roxom-markets/schemas` enums and existing publishers.

### 2. Pick repo pattern

| Repo | Harness entry | Reference |
|------|---------------|-----------|
| **roxtarsverse** (`apps/tx`, other apps) | `createTestComponents` + domain helper | [reference.md § Roxtarsverse](reference.md#roxtarsverse) |
| **hermod** | `createHermodTestApp` | [reference.md § Hermod](reference.md#hermod) |
| **Other Roxom service** | Find `tests/components.ts` or `create*TestApp`; if missing, mirror tx or hermod | [reference.md § Adopting](reference.md#adopting-in-a-new-repo) |

### 3. Pick integration tier

Use the **smallest tier** that can prove the behavior:

| Tier | Real | Mock/stub | Use when |
|------|------|-----------|----------|
| **DB + services** | Postgres, real repos/services | externals, optional rabbit/grpc | Service/repository behavior, SQL state |
| **DB + handler/RPC** | above + real handler factory | externals at component boundary | Rabbit RPC ingress (tx pattern) |
| **DB + gRPC** | Postgres + gRPC server + generated client | externals | gRPC contract + persistence |
| **DB + Rabbit consumer** | Postgres + real broker + app boot (`main()`) | server/http | Inbound queue → DB → outbound fan-out (hermod) |
| **DB + Rabbit producer** | above + Hermod client route + `publish` spy | externals | Outbound Hermod notification (tx producer) |

**Rule:** Do not wire Hermod/Rabbit extras into the default stack when error-path tests do not need them. Add a **notification-aware** or **rabbit-aware** stack variant (see tx `createInternalTransferNotificationStack`).

### 4. Register isolated resources

Every suite needs **unique** resources when Jest runs in parallel:

- **DB name:** register in `TEST_CONFIGS` (tx) or pass a dedicated `databaseName` (hermod).
- **gRPC port:** unique per suite in tx `TEST_CONFIGS`; hermod often uses random port — prefer fixed unique port in CI-heavy suites.
- **Rabbit vHost:** one vHost per rabbit-tier suite (hermod); tx can use `rabbitVHost` on `createTestComponents` when needed.

Lifecycle template:

```text
beforeAll  → create harness (60s timeout)
beforeEach → clear mocks, re-apply spy defaults, reset/seed DB
afterAll   → stop components/app → drop test database (30s timeout)
```

### 5. Build the harness

**Roxtarsverse (tx-style)**

1. `createTestComponents({ databaseName, grpcPort?, rabbitVHost? })`
2. Wire `initRepositories` → services → handler(s) with the **smallest** real graph.
3. For notification tests: register Hermod route, replace `rabbitmq.client`, spy `publish`.
4. Export from `tests/integration/helpers/<domain>Context.ts`:
   - stack factory(ies) — minimal vs extended
   - `reset*Tables`, seed helpers, message builders
   - assertion helpers (`findHermodPublish`, etc.)

**Hermod**

1. `createHermodTestApp({ databaseName, grpcPort? })` or `{ rabbitVHost }` for full consumer path.
2. Seed via **real services** inside transactions.
3. Assert with SQL + optional gRPC client + Rabbit probes.

See [reference.md](reference.md) for file paths and copy-paste skeletons.

### 6. Seed data

| Data | Prefer |
|------|--------|
| Users, accounts, addresses | Parameterized SQL via harness helpers |
| Balances / movements | Real `movementsService.storeMovements` when balance matters |
| Stable IDs (instruments, networks) | Shared fixtures (`SAMPLE_INSTRUMENT_IDS`, not `'btc-1'`) |
| Cross-user scenarios | Explicit seed helpers with docstring explaining why |

Order deletes to respect FKs. Reset in `beforeEach` for isolation.

### 7. Trigger and assert

**Trigger:** Call the same ingress production uses — handler with `RabbitMessage`, gRPC client method, or publish to queue (consumer tests).

**Assert layers (pick what the test claims to prove):**

1. **Handler/service result** — `expect(result.error).toBe(false)`
2. **DB state** — SQL on domain tables (`tx_internal`, `user_notifications`, …)
3. **gRPC response** — typed client response fields
4. **Rabbit producer** — spy on `rabbitmq.client.publish` or `publishToTopic`
5. **Rabbit consumer** — queue drain, topic probe, outbound spy

**Producer async fan-out (tx → Hermod):**

```typescript
await waitUntil(() =>
  Boolean(findHermodPublish(publishSpy, { userId, direction: 'sent' }))
);
const call = findHermodPublish(publishSpy, { userId, direction: 'sent' });
expect(call).toEqual([expect.objectContaining({ request_id: expect.any(String) }), 'hermod', expect.objectContaining({ /* contract */ })]);
```

Spy at the **last in-process boundary** before the message leaves the service. Use a named lookup helper instead of raw `mock.calls[n][2]`.

**Consumer async (hermod):** `waitForQueueConsumer` → publish → `waitForQueueDrain` → SQL assert → optional `waitForTopicMessage` / `publishToTopic` spy.

### 8. Verify

From the correct package root:

```bash
# tx — single suite, serial (recommended while authoring)
yarn --cwd "/path/to/roxtarsverse" workspace tx test tests/integration/flows/<file>.integration.test.ts --runInBand

# hermod — explicit path (integration project also matches tests/unit)
yarn --cwd "/path/to/hermod" test:integration --runInBand tests/integration/<file>.integration.test.ts
```

**Prerequisites:** `tests/env/.env` from `.env.example`; local Postgres; RabbitMQ (+ management plugin for vHost suites); Redis when the harness starts it.

If parallel runs fail with `unique_violation` on template DB or `EADDRINUSE` on gRPC, rerun with `--runInBand`.

### 9. Deliver

When using `/bmo-step-deliver`, typical commit split:

1. `test(<app>): Add <domain> integration harness` — configs, helpers, seeds
2. `test(<app>): Cover <behavior> integration` — spec file(s)
3. `fix(<app>): …` — only if the test exposed a production bug (separate commit)

---

## Design rules

1. **Smallest real stack** — no full app boot unless the test needs it (hermod rabbit tier).
2. **One assertion seam per concern** — DB proof vs Rabbit proof can be separate tests.
3. **No `any` in new test code** — type Rabbit tuples narrowly (`HermodPublishCall`).
4. **Re-apply mocks after `jest.clearAllMocks()`** — unleash, lockManager, pricetrox, etc.
5. **Do not assert Rabbit synchronously** after fire-and-forget handler returns.
6. **Fixture realism** — UUID v4/v7, real enum members, plausible amounts.
7. **Name files honestly** — `*.integration.test.ts` when using global DB setup; scope in filename (`notifications.rabbit.integration.test.ts`).
8. **Document harness variants** — short docstring on why minimal vs notification stack exist.

---

## Anti-patterns

| Avoid | Do instead |
|-------|------------|
| Mock `userEventsService` when testing Hermod publish | Wire real `userEventsService` + spy `publish` |
| Share one gRPC port across suites | Unique port per suite or `--runInBand` |
| Inline 80-line seed in every test | Harness seed helper |
| `integration/grpcHandlers/` (mocked) for real gRPC proof | `integration/grpc/` with real server |
| Commit `file:.yalc/...` lockfile drift | Keep local schema links unstaged |
| Over-broad `test:integration` on hermod | Pass explicit file path |

---

## Canonical examples

| Scenario | File |
|----------|------|
| tx: Hermod producer, RPC ingress, `waitUntil` | `roxtarsverse/apps/tx/tests/integration/flows/internalTransferNotifications.integration.test.ts` |
| tx: harness + seeds + publish spy | `roxtarsverse/apps/tx/tests/integration/helpers/internalTransferHandlerContext.ts` |
| tx: full deposit flow + `publishToTopic` | `roxtarsverse/apps/tx/tests/integration/flows/deposits.test.ts` |
| tx: real gRPC server + client | `roxtarsverse/apps/tx/tests/integration/grpc/tx/getLimit.test.ts` |
| hermod: DB + service | `hermod/tests/integration/notifications.integration.test.ts` |
| hermod: gRPC | `hermod/tests/integration/notifications.grpc.integration.test.ts` |
| hermod: Rabbit consumer + topic probe | `hermod/tests/integration/notifications.rabbit.integration.test.ts` |

More paths and skeletons: [reference.md](reference.md).
