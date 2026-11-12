# Database review rules (`database`)

Apply when the diff touches SQL queries, repositories/stores, database transactions, schema constraints, or migrations.

## 1. Strict issues (`[issue]`)

Check these first. Every violation is a connection/lock hazard, data-integrity gap, or avoidable hot-path overhead.

- **[validate-before-transaction]** Run format and precondition validation before opening a database transaction so invalid requests never acquire or hold scarce connections.
- **[no-transaction-for-single-read]** Execute single-query reads through the standard non-transaction query path rather than wrapping a single `SELECT` in a transaction.
- **[db-constraint-matches-service-rule]** Pair any service-enforced format rule with an identical database `CHECK` constraint so other writers cannot insert invalid rows.
- **[sql-alias-instead-of-row-map]** Alias SQL columns to application field names (`SELECT col AS "fieldName"`) directly in the query instead of mapping every row in application code after fetch.

## 2. Style & conventions (`[style]`)

Check these after Pass 1. Align the code to these patterns without crowding out `[issue]` findings.

- **[skip-empty-table-backfill]** Add a `NOT NULL` column in a single migration step without an `UPDATE` backfill when both production and fresh migration runs start with an empty table.
- **[single-use-vendor-error-codes]** Hardcode a single-use vendor `SQLSTATE` literal at the catch site with a comment linking the vendor docs, extracting a shared constant only when multiple sites check the same code.
- **[no-custom-uuid-guards]** Rely on database `uuid` column types and existing boundary mappers instead of adding custom UUID regex helpers inside repository paths.
