---
id: 20260910T190617Z-roxom-markets-window-pr803
status: actioned
capturedAt: 2026-09-10T19:06:17Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/window#803
prUrl: https://github.com/roxom-markets/window/pull/803
fixCommitSha: e1bd2306811507635555382bc23c4f5bdd156886
threadCount: 7
---

# Session capture — roxom-markets/window#803

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOMvQwAc6hJXWP |
| **path** | src/routes/handlers/transactions/addressBook/handlers.ts |
| **line** | 33 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | src/routes/handlers/transactions/addressBook/resolveDestination.ts, src/routes/handlers/transactions/addressBook/listWithdrawalAddressBook.handler.ts, src/routes/handlers/transactions/addressBook/saveWithdrawalAddress.handler.ts |

### Reviewer comment

Not sure about this method or logic. Because it allows passing the instrument id and network id to return the instrument id and network id :/

### Resolution

Valid. Destination lookup now uses the field that was sent: instrumentId goes to getInstrumentById, asset to getInstrumentBySymbol, and network still goes through resolveKnownNetworkId. Save returns networkId as a string with no cast.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOMvQwAc6hJcha |
| **path** | src/routes/handlers/transactions/addressBook/errors.ts |
| **line** | 29 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | src/routes/handlers/transactions/addressBook/errors.ts, tests/unit/addressBook.handlers.test.ts |

### Reviewer comment

Why is the invalid user a 500?

### Resolution

Valid. INVALID_USER is 401 via unauthorized() after logging tx's message. Window already 401s a missing session user; tx rejecting that same identity is auth, not a 5xx.

## Thread 3

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOMvQwAc6hJgrs |
| **path** | src/helpers/resolveInstrument.ts |
| **line** | 1 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | src/helpers/resolveInstrument.ts, src/routes/handlers/instruments/getInstrumentBySymbol.handler.ts, src/routes/handlers/transactions/addressBook/resolveDestination.ts |

### Reviewer comment

I don't believe that we need this method. It adds another layer of abstraction to our instrument getters which we have many.
Also this method assumes that an invalid UUID is a symbol which might not be true.

### Resolution

Valid. Removed resolveInstrumentByIdOrSymbol. Address book looks up by field instead of sniffing UUID shape; the instruments route keeps its local isValidUuid branch to pick getInstrumentById vs getInstrumentBySymbol.

## Thread 4

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOMvQwAc6hJkBn |
| **path** | src/routes/handlers/transactions/addressBook/handlers.ts |
| **line** | 29 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | src/routes/handlers/transactions/addressBook/listWithdrawalAddressBook.handler.ts, src/routes/handlers/transactions/addressBook/saveWithdrawalAddress.handler.ts, src/routes/handlers/transactions/addressBook/renameWithdrawalAddress.handler.ts, src/routes/handlers/transactions/addressBook/deleteWithdrawalAddress.handler.ts, src/routes/handlers/transactions/addressBook/setWithdrawalAddressWhitelisted.handler.ts, src/routes/handlers/transactions/addressBook/getWithdrawalSecuritySettings.handler.ts, src/routes/handlers/transactions/addressBook/setWithdrawalWhitelistEnabled.handler.ts |

### Reviewer comment

I don't think that this method adds real value, it seems like an unnecessary abstraction.

### Resolution

Valid. Removed resolveUserId. Each handler reads req.sessionHeaders?.user?.id inline, matching the other HTTP handlers.

## Thread 5

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOMvQwAc6hL0gH |
| **path** | src/routes/handlers/transactions/addressBook/formatEntry.ts |
| **line** | 25 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | src/routes/handlers/transactions/addressBook/formatEntry.ts |

### Reviewer comment

Is there a significant difference or reason why we differentiate between the WithdrawalAddressBookEntry type and the new type we create AddressBookEntryPayload? This type of mapping tends to drift away and we end up with two different interfaces for the same entity.

### Resolution

Valid. Replaced the restated AddressBookEntryPayload with AddressBookHttpEntry derived from WithdrawalAddressBookEntry, plus the HTTP display fields and nulls for proto optionals. userId is still stripped.

## Thread 6

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOMvQwAc6hL-t2 |
| **path** | src/routes/handlers/transactions/resolveWithdrawalDestination.ts |
| **line** | 40 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | src/routes/handlers/transactions/resolveWithdrawalDestination.ts |

### Reviewer comment

Why do we default to undefined? The only case that would default to undefined seems to be an empty `string` but `instrumentId` validation should happen beforehand, not in this method.

### Resolution

Valid. Removed instrumentId || undefined. withdrawalNetworksFor now treats only undefined as every network; a provided string, including empty, goes to getInstrumentById.

Block review finding applied: the helper still collapsed empty string via truthiness; switched the all-networks branch to `instrumentId === undefined`.

## Thread 7

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOMvQwAc6hMFN2 |
| **path** | src/routes/handlers/transactions/addressBook/handlers.ts |
| **line** | 1 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | src/routes/handlers/transactions/addressBook/index.ts, src/routes/handlers/transactions/addressBook/listWithdrawalAddressBook.handler.ts, src/routes/handlers/transactions/addressBook/saveWithdrawalAddress.handler.ts, src/routes/handlers/transactions/addressBook/renameWithdrawalAddress.handler.ts, src/routes/handlers/transactions/addressBook/deleteWithdrawalAddress.handler.ts, src/routes/handlers/transactions/addressBook/setWithdrawalAddressWhitelisted.handler.ts, src/routes/handlers/transactions/addressBook/getWithdrawalSecuritySettings.handler.ts, src/routes/handlers/transactions/addressBook/setWithdrawalWhitelistEnabled.handler.ts, src/routes/handlers/transactions/addressBook/gate.ts |

### Reviewer comment

We usually have different files for each handler. It makes it easier to test, track, and read.

### Resolution

Valid. Split handlers.ts into one *.handler.ts per endpoint. index.ts remains the barrel; gate, errors, schemas, and destination lookup stay local.
