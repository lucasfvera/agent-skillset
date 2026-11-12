# Linear adapter (`bmo-triage`)

Load this file only when `$ARGUMENTS` is a `linear.app` URL or a team issue key (`ENG-123`, `ROX-456`, etc.).

## Fetch steps

1. **Identifier:** Extract the team key (`[A-Z]{2,10}-\d+`, uppercase) from the URL or `$ARGUMENTS`.
2. **Fetch:** Query issue details via the host's configured **Linear MCP** tools (or a local Linear CLI if installed).
   - If authentication is required and the host exposes an MCP auth flow, authenticate once and retry.
   - **Fallbacks:** if Linear tools are unavailable or unauthenticated, check for a linked GitHub issue/PR via `gh`, or ask the user once to paste the issue title + description (or record `Skip — unreachable` in Step 2 when running unattended).
3. **Fields to map:**
   - **Status & terminal check:** Linear `state.type` (`completed` or `canceled` is terminal) plus `state.name`.
   - **Priority:** Linear priority label (`Urgent` → High importance; `High` → Medium/High importance; `Medium` / `Low` / `No priority` → Low unless due date / SLA / incident labels bump it).
   - **Context:** `title`, `description`, `labels`, recent `comments`, `attachments` / linked GitHub PRs, `project` / `team`, `dueDate` / active cycle.

**Done:** Linear issue fields are mapped for `bmo-triage` Step 2, or fetch failure is recorded.
