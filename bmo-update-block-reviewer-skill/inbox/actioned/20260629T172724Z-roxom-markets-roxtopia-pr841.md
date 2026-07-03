---
id: 20260629T172724Z-roxom-markets-roxtopia-pr841
status: actioned
capturedAt: 2026-06-29T17:27:24Z
actionedAt: 2026-07-01T19:18:27Z
pr: roxom-markets/roxtopia#841
prUrl: https://github.com/roxom-markets/roxtopia/pull/841
fixCommitSha: 0f40896b0378076b9fbff3cf0a2bb0609d5eb710
threadCount: 4
sourceTranscript: 83a3d64a-e923-4b32-ae51-a6f377a1cfc3
backfillNote: Backfilled from agent transcript + GitHub resolved threads (pre-inbox capture).
---

# Session capture — roxom-markets/roxtopia#841

Backfilled from agent transcript + GitHub resolved threads (pre-inbox capture).

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6NClFo |
| **path** | `apps/exchange/src/components/common/TpSlModal/TpSlModal.tsx` |
| **line** | — |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

Is there a way to avoid this useEffect? What you are doing here is not a side effect and we might not need it. Also refs tend to introduce more problems than solutions so avoid them if possible.

### Resolution

Valid. Removed the `useEffect` and `wasOpenRef`. Form state now syncs via react-hook-form's `values: open ? tpSlFormValues : undefined`, which repopulates fields when the modal opens without an imperative side effect.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6NClvZ |
| **path** | `apps/exchange/src/components/common/TpSlModal/TpSlModal.tsx` |
| **line** | — |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

We should never use loose equiality.

### Resolution

Valid. Replaced loose `!= null` checks with strict `!== undefined` in `buildTpSlFormValues` and `isEditMode`.

## Thread 3

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6NDDhG |
| **path** | `apps/exchange/src/components/common/TpSlModal/TpSlModal.tsx` |
| **line** | — |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

Not sure what's the intention behind this new parameter in the method. It seems that it is leftover from the prev implementation. Is that so? Or we need it?

### Resolution

Valid. The inline object passed to `buildTpSlFormValues` and the `handleOpenChange` reset were leftovers from the earlier `values`/ref approach. Removed both: we pass `currentTpSl` directly again and wire `Dialog` to `onOpenChange` — remount via `isModalOpen` in the parent key handles fresh defaults on open.

## Thread 4

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6NDEUI |
| **path** | `apps/exchange/src/components/PositionsTable/TpSlPositionButton.tsx` |
| **line** | 1 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

Isn't there an existing value that we could use to generate this key instead of creating a new state in the component?

### Resolution

Valid. Dropped `modalOpenSession` and use existing `isModalOpen` in the modal `key` (`${tpOrderId}-${slOrderId}-${isModalOpen}`). That remounts when the dialog opens without extra state.
