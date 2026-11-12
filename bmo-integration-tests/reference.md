# Integration test blueprints

Disclosed patterns for [`bmo-integration-tests`](SKILL.md). Adapt idioms to the repository's language, test runner, ORM/SQL client, and broker SDK.

---

## 1. Tiered harness factory

Keep the default harness fast (DB + core dependencies) and opt into transport or broker wiring only in suites that exercise those boundaries:

```typescript
export interface TestHarnessOptions {
  databaseName: string;
  enableRpcServer?: boolean;
  brokerNamespace?: string; // vHost, topic prefix, or queue namespace
}

export async function createTestHarness(opts: TestHarnessOptions) {
  const db = await cloneOrMigrateTestDb(opts.databaseName);

  // Stub only external third-party boundaries the service does not own
  const externalGateway = createExternalGatewayStub();

  const broker = opts.brokerNamespace
    ? await startRealBrokerClient({ namespace: opts.brokerNamespace })
    : createNoopBrokerStub();

  const repos = createRepositories(db);
  const services = createServices({ repos, broker, externalGateway });

  const rpc = opts.enableRpcServer
    ? await startRpcServerAndClient({ host: '127.0.0.1', port: 0, services }) // port 0 = ephemeral
    : undefined;

  return {
    db,
    broker,
    rpc,
    repos,
    services,
    externalGateway,
    async stop() {
      await rpc?.close();
      await broker.close();
      await db.destroyAndDrop();
    },
  };
}
```

### Key invariants

- **Ephemeral ports (`port: 0`)** eliminate `EADDRINUSE` across parallel workers; read the bound port from the server listener and pass it to the test client.
- **Explicit teardown order:** stop ingress servers and queue consumers **before** closing broker channels or dropping the database so in-flight handlers do not throw post-test connection errors.

---

## 2. Database isolation strategies

Pick the strategy matching the repo's existing tooling (check existing suites first):

| Strategy | Best when | Parallel safety | Caveat |
|----------|-----------|-----------------|--------|
| **Template DB clone** (`CREATE DATABASE test_x TEMPLATE test_template`) | Postgres / SQL suites with many migrations | High (unique DB name per suite) | Global setup must migrate `test_template` once before workers fork; terminate connections before `CLONE`/`DROP` |
| **Per-suite schema** (`search_path = suite_<id>`) | Single shared Postgres instance without superuser `CREATEDB` | High | Ensure queries do not hardcode `public.` |
| **Testcontainers** (per-worker or shared container + per-suite DB) | Docker available in local + CI | High | Reuse container across suites in one run; isolate via DB/schema inside it |
| **Per-test transaction rollback** | Fast repository-only tests on a single DB connection | High | Cannot test explicit `COMMIT`/`ROLLBACK` handling or cross-connection visibility (HTTP/RPC server using a pool) |

**Resetting between tests (`beforeEach`):**

- Truncate `RESTART IDENTITY CASCADE` or delete in reverse foreign-key order.
- Re-apply default stub behaviors immediately after `clearAllMocks()`.

---

## 3. Broker & async event patterns

### Bounded condition polling (`waitUntil`)

Never assert fire-and-forget side effects synchronously after the ingress call returns, and never coordinate tests with fixed `sleep(500)` delays:

```typescript
export async function waitUntil<T>(
  probe: () => T | undefined | false | Promise<T | undefined | false>,
  { timeoutMs = 5_000, intervalMs = 50 } = {},
): Promise<T> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const value = await probe();
    if (value) return value;
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  throw new Error(`waitUntil timed out after ${timeoutMs}ms`);
}
```

### Pattern A — Producer boundary (service publishes event/command)

Wire the real domain service and real serialization/publisher layer, then spy or capture at the **last in-process broker client method** before network I/O (or bind an ephemeral test queue to the real exchange):

```typescript
const publishSpy = vi.spyOn(harness.broker, 'publish');

await harness.rpc!.client.transferFunds({ fromAccountId, toAccountId, amountCents: 25_00 });

const published = await waitUntil(() =>
  findPublishedEvent(publishSpy, { topic: 'ledger.transfer.completed', accountId: fromAccountId }),
);
expect(published).toMatchObject({
  eventVersion: 1,
  accountId: fromAccountId,
  amountCents: 25_00,
});
```

- Encapsulate call matching in a typed helper (`findPublishedEvent`) rather than indexing `publishSpy.mock.calls[0][2]`, so unrelated telemetry or ordering changes do not make assertions brittle.

### Pattern B — Consumer boundary (service consumes queue/stream)

1. Boot the real consumer loop against an isolated queue/topic namespace.
2. Wait until the consumer subscription is active before publishing the test message.
3. Publish a schema-valid (or intentionally malformed, for DLQ/poison-message tests) payload.
4. Poll with `waitUntil` until the persisted DB state or ack/DLQ metric settles.
5. When asserting downstream fan-out topics, open a **dedicated probe channel/consumer** separate from the service's worker channel.

### Cross-service contract rule

Avoid booting Service A and Service B in the same integration suite unless testing a dedicated end-to-end environment:

- **Service A integration test** proves the **producer boundary** against the shared schema/proto/OpenAPI contract.
- **Service B integration test** feeds that exact contract shape into its **consumer boundary** and proves persistence + downstream effects.

---

## 4. Bootstrapping a repo with no integration harness

1. Document required local services and defaults in `.env.example` / `docker-compose.test.yml` (or wire Testcontainers).
2. Add a dedicated runner target (e.g. `test:integration`) separate from fast unit tests so unit runs stay zero-infra.
3. Create global/suite DB migration bootstrap + `createTestHarness` with minimal defaults.
4. Add shared seed builders and `waitUntil` under `tests/integration/helpers/`.
5. Name specs clearly (`*.integration.test.*` / `*_integration_test.*`) so CI and developers can target them explicitly.

## Pre-PR checklist

- [ ] `.env.example` / Compose / Testcontainers config covers any new infra env vars
- [ ] Unique DB/schema, ephemeral port, and isolated queue/topic namespace per suite
- [ ] `beforeEach` resets state and re-applies default external-stub return values
- [ ] `afterAll` stops servers/consumers before closing broker/DB connections
- [ ] Async side effects synchronized with bounded `waitUntil` (no bare timer sleeps)
- [ ] No `any` in fixtures or assertions; named helpers for broker payload lookup
