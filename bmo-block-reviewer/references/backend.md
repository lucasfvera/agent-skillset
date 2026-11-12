# Backend review rules (`backend`)

Apply when the diff touches HTTP/gRPC/message handlers, routes, middleware, services, wire schemas/protos, or generated clients.

## 1. Strict issues (`[issue]`)

Check these first. Every violation is a boundary contract bug, security/error leak, or build hazard.

- **[validate-inbound-ids-at-handler]** Validate inbound ID formats (such as UUIDs) at the handler boundary and return the domain 4xx invalid-ID error before calling the service or store.
- **[generic-errors-to-callers]** Return a generic internal error message to callers on unmapped failures and log the full error details server-side only, never leaking raw database or driver errors.
- **[map-upstream-errors-to-http]** Map client/validation failures to `4xx`, local service faults to `5xx`, and upstream/transport failures to `502` at the HTTP boundary without forwarding internal proto codes in the HTTP body.
- **[auth-identity-is-401]** Map upstream rejection of the caller's session identity to `401 Unauthorized`, not `500`.
- **[keep-proto-success-envelopes]** Preserve existing `{ success, data?, error? }` proto response envelopes across sibling RPCs rather than flattening a single payload field onto the top-level response.
- **[reproducible-codegen-config]** Fix the code generator configuration so generated clients are reproducible; never hand-edit generated files.
- **[dispatch-by-sent-field]** Resolve lookups from the explicit field the caller populated rather than sniffing UUID format or echoing unmatched IDs back unchanged.
- **[shared-error-constants]** Map and compare errors using shared constants or typed error classes on both producer and consumer rather than comparing free-form error strings.

## 2. Style & conventions (`[style]`)

Check these after Pass 1. Align the code to these patterns without crowding out `[issue]` findings.

- **[match-sibling-route-registration]** Register routes, middleware, and handlers using the same shape as sibling endpoints in the router file, adding extra middleware or wrappers only when this endpoint requires them.
- **[one-handler-per-file]** Place each HTTP or gRPC endpoint handler in its own dedicated file rather than bundling multiple endpoints together.
- **[colocate-handler-schemas]** Place request validation schemas in a sibling schema file beside the handler, matching the existing handler directory layout.
- **[match-generated-client-calls]** Call generated clients with the exact signature sibling handlers use, without attaching extra tracing or metadata arguments the client contract does not expect.
- **[derive-http-types-from-domain]** Derive HTTP projections from the canonical domain type (`Pick`, `Omit`, or mapper types) instead of redeclaring a parallel interface for the same entity.
- **[zod-parse-contract-payload]** Validate and strip boundary payloads by parsing with the existing Zod schema rather than manually remapping successful contract payloads field-by-field.
- **[no-wire-type-paths]** Implement code paths only for wire types the upstream producer actually sends, omitting branches for unused union members.
