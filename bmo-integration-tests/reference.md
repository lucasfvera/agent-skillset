# Integration test reference

Repo-specific paths, skeletons, and tier details for `bmo-integration-tests`.

---

## Roxtarsverse

**Primary example app:** `apps/tx`

### Key files

| Path | Role |
|------|------|
| `apps/tx/jest.config.js` | Default: `globalSetup`/`globalTeardown`, `maxWorkers: 4` |
| `apps/tx/jest.setup.ts` | Creates `test_tx_template`, runs migrations once |
| `apps/tx/jest.teardown.ts` | Drops `test_tx_*` databases |
| `apps/tx/tests/setup.ts` | `setupDatabase`, `dropDatabase`, clone from template |
| `apps/tx/tests/components.ts` | `createTestComponents`, `stopTestComponents`, `TEST_DB_PREFIX` |
| `apps/tx/tests/constants/configs.ts` | `TEST_CONFIGS` — `{ dbName, grpcPort }` per suite |
| `apps/tx/tests/mocks/data/instruments.ts` | `SAMPLE_INSTRUMENT_IDS`, `SAMPLE_NETWORKS` |
| `apps/tx/tests/integration/helpers/internalTransferHandlerContext.ts` | Domain harness (stacks, seeds, spy) |
| `apps/tx/tests/integration/flows/internalTransferNotifications.integration.test.ts` | Producer notification spec |
| `libs/waitUntil/index.ts` | Sync condition poll (100ms, 10s timeout) |

### `createTestComponents` behavior

- **Real:** `logger`, `server`, `grpc`, `rabbitmq`, `pg`, `redis`, `lockManager`, …
- **Mocked externals:** `fireblocks`, `gayway`, `instruments`, `pricetrox`, `yuta`, `trm`, `tribunal`, `unleash`, `activity`
- DB: `test_tx_${databaseName}` cloned from template
- gRPC: `createGrpcComponent({ host: '127.0.0.1', port: grpcPort })` when port set
- Rabbit: real broker; optional `rabbitVHost` creates isolated vHost via Management API (`:15672`)

### Harness skeleton (tx RPC + Hermod producer)

```typescript
// tests/constants/configs.ts — add entry
myFeatureNotifications: { dbName: 'my_feature_notif', grpcPort: 50069 },

// tests/integration/helpers/myFeatureContext.ts
export async function createMyFeatureNotificationStack(config: {
  databaseName: string;
  grpcPort: number;
}): Promise<MyFeatureNotificationStack> {
  const testComponents = await createTestComponents(config);
  // ... initRepositories, services ...

  testComponents.rabbitmq.setClientRoutes([
    { name: RabbitClients.HERMOD, mode: 'pub', queue: RabbitEvents.HERMOD.CREATE_NOTIFICATION },
  ]);
  testComponents.rabbitmq.client = await testComponents.rabbitmq.setClientRoutes(/* ... */).createRouter();
  const publishSpy = jest.spyOn(testComponents.rabbitmq.client!, 'publish');

  const userEventsService = createUserEventsService({ /* real chain */ });
  // rebuild service with real userEventsService
  return { testComponents, publishSpy, /* handlers */ };
}
```

### Spec skeleton (tx)

```typescript
const { dbName, grpcPort } = TEST_CONFIGS.INTEGRATION.FLOWS.myFeatureNotifications;

describe('my feature Hermod notifications (integration)', () => {
  let stack: MyFeatureNotificationStack;

  beforeAll(async () => {
    stack = await createMyFeatureNotificationStack({ databaseName: dbName, grpcPort });
  }, 60_000);

  afterAll(async () => {
    await stopTestComponents(stack.testComponents);
    await dropDatabase(`${TEST_DB_PREFIX}${dbName}`);
  }, 30_000);

  beforeEach(async () => {
    jest.clearAllMocks();
    jest.spyOn(stack.testComponents.unleash, 'isEnabled').mockReturnValue(true);
    applyDefaultPricetroxMocks(stack.testComponents);
    await resetMyFeatureTables(stack.testComponents.pg);
    await seedMyFeatureScenario(stack);
  });

  it('publishes expected Hermod message', async () => {
    const result = await handler(buildRabbitMsg());
    expect(result.error).toBe(false);

    await waitUntil(() => Boolean(findHermodPublish(stack.publishSpy, { userId, direction: 'sent' })));
    expect(findHermodPublish(stack.publishSpy, { userId, direction: 'sent' })).toEqual([/* contract */]);
  });
});
```

### gRPC skeleton (tx)

See `apps/tx/tests/integration/grpc/tx/getLimit.test.ts`:

- `createTestComponents({ databaseName, grpcPort })`
- Register handler via `createTypedService` / `grpcRoutes`
- `grpc.start()` in `beforeAll`
- Connect with generated `*ServiceClient` + `ChannelCredentials.createInsecure()`

### Run commands (tx)

```bash
yarn --cwd "/Users/lucasferreyravera/roxom/roxtarsverse" workspace tx test tests/integration/flows/myFeature.integration.test.ts --runInBand
yarn --cwd "/Users/lucasferreyravera/roxom/roxtarsverse" workspace tx test:unit          # no Postgres
yarn --cwd "/Users/lucasferreyravera/roxom/roxtarsverse" workspace tx test:grpc-handlers # mocked, no DB
```

### tx pitfalls

- Port collisions in `TEST_CONFIGS` → `EADDRINUSE`; assign unique ports or `--runInBand`
- Template clone races → `unique_violation`; serial run or ensure teardown
- `jest.clearAllMocks()` clears call history but keeps spies — re-apply `mockReturnValue`
- `integration/grpcHandlers/` is **mocked**; real gRPC is under `integration/grpc/`
- `TEST_DB_PREFIX` is `test_tx_` — use `${TEST_DB_PREFIX}${dbName}` in `dropDatabase`

---

## Hermod

### Key files

| Path | Role |
|------|------|
| `jest.config.js` | Projects: `unit` \| `integration` |
| `jest.setup.ts` / `jest.teardown.ts` | `test_hermod_template` lifecycle |
| `tests/setup.ts` | Clone/drop per suite |
| `tests/helpers/hermodTestApp/createHermodTestApp.ts` | Tiered app harness |
| `tests/helpers/hermodTestApp/rabbitManagement.ts` | vHost via Management API |
| `tests/helpers/waitUntil.ts` | Async poll returning `T \| undefined` |
| `tests/integration/notifications.integration.test.ts` | DB tier |
| `tests/integration/notifications.grpc.integration.test.ts` | gRPC tier |
| `tests/integration/notifications.rabbit.integration.test.ts` | Rabbit consumer tier |

### `createHermodTestApp` tiers

| Config | Boots |
|--------|-------|
| `{ databaseName }` | Real PG + full `AppContainer`; stubs redis/rabbit/server/grpc |
| `{ databaseName, grpcPort }` | PG + real gRPC + client; stubs redis/rabbit/server |
| `{ databaseName, rabbitVHost }` | PG + real Rabbit + Redis + `main()` full wiring |

Env snapshot/restore on stop. Always call `stopHermodTestApp(testApp)` in `afterAll`.

### Rabbit consumer helpers (from hermod rabbit suite)

- `waitForQueueConsumer(channel, queueName)`
- `waitForQueueDrain(channel, queueName)`
- `createTopicProbe(connection, routingKey)`
- `waitForTopicMessage(probeChannel)`
- `jest.spyOn(rabbitmq.client, 'publishToTopic')` for outbound fan-out

Use a **second channel** for topic probes — consumer channel stays busy.

### Spec skeleton (hermod DB)

```typescript
describe('notifications (integration)', () => {
  let testApp: HermodTestApp;

  beforeAll(async () => {
    testApp = await createHermodTestApp({ databaseName: 'notifications' });
  }, 60_000);

  afterAll(async () => {
    await stopHermodTestApp(testApp);
  }, 30_000);

  beforeEach(async () => {
    await testApp.appContainer.components.pg.queryWithoutTransaction(
      'DELETE FROM user_notification_events; DELETE FROM user_notifications;'
    );
  });

  it('persists notification', async () => {
    const tx = await testApp.appContainer.components.pg.startTransaction();
    const result = await testApp.appContainer.services.notificationsService.createNotification(/* ... */, tx);
    expect(result.error).toBe(false);
    await tx.commit();
    // SQL assert
  });
});
```

### Run commands (hermod)

```bash
yarn --cwd "/Users/lucasferreyravera/roxom/hermod" test:integration --runInBand tests/integration/notifications.rabbit.integration.test.ts
```

**Note:** `yarn test:integration` without a path also matches `tests/unit/**` — always pass an explicit file.

### hermod pitfalls

- Rabbit tier needs Rabbit **management plugin** (port 15672) for vHost creation
- `jest.resetModules()` + dynamic import required so env mutations apply before init
- Malformed queue messages: assert no DB rows + no outbound publish after short sleep

---

## Adopting in a new repo

1. **Find or create** `tests/env/.env.example` with `DATABASE_URL`, `RABBITMQ_URL`, `GRPC_*`.
2. **Add** `jest.setup.ts` / `jest.teardown.ts` with template DB + migrations (copy tx or hermod).
3. **Add** `tests/setup.ts` with `setupDatabase` / `dropDatabase` / `buildDatabaseUrl`.
4. **Add** `createTestComponents` or `create*TestApp`:
   - Real: pg, rabbitmq, grpc (as needed)
   - Mock: every external adapter the service calls
5. **Register** unique `databaseName` (+ port/vHost) per suite.
6. **Place specs** under `tests/integration/` with `*.integration.test.ts` suffix.
7. **Document** prerequisites in app `README.md`.

**Producer vs consumer:**

- Service **publishes** to Hermod (tx, roxtars, …) → spy `publish`, register Hermod client route.
- Service **consumes** from Rabbit (hermod) → boot `main()`, publish to queue, drain, assert DB + optional topic probe.

---

## Producer ↔ consumer cross-service tests

For tx → hermod flows, **do not** run both services in one Jest suite unless explicitly required.

**Preferred:** tx integration test asserts **producer boundary** (`publish` spy with `Notification.Types.*` contract). hermod integration test asserts **consumer boundary** (queue → DB → topic). Contract source: `roxtarsverse/docs/csv-hermod-notification-mapping.md` and `@roxom-markets/schemas` `Notification` types.

---

## Checklist before opening PR

- [ ] `tests/env/.env.example` documents new env vars (if any)
- [ ] Unique `dbName` / `grpcPort` / `rabbitVHost` registered
- [ ] `beforeEach` isolation (truncate or re-seed)
- [ ] `afterAll` stops components and drops DB
- [ ] Targeted test run with `--runInBand` attached to PR test plan
- [ ] No `any` in new assertions; named helpers for Rabbit tuple lookup
- [ ] Harness docstrings explain minimal vs extended stack
