# Testing review rules (`testing`)

Apply when the diff touches unit, component, or integration tests (`*.test.*`, `*.spec.*`), test fixtures, mocks, or suite harnesses.

## 1. Strict issues (`[issue]`)

Check these first. Every violation produces flaky tests, parallel worker collisions, or false-positive specs that pass while production is broken.

- **[no-settimeout-sleeps]** Await the returned promise, event helper, or explicit stability signal directly in unit tests; never pause with `setTimeout` timer sleeps.
- **[test-contract-types]** Type test fixtures and mock payloads with the producing service's real contract types rather than loose object shapes so contract drift fails at compile time.
- **[integration-tests-match-production]** Drive integration tests through the shared suite factory and generated client the way production calls the API, rather than calling handlers directly, booting a parallel harness, or wrapping the client in test-only promises.
- **[shared-test-config-ports]** Register a distinct integration listen port per suite in the shared test config map rather than hardcoding ports in specs or sharing one port across parallel workers.
- **[test-unit-owned-contract]** Assert the contract owned by the unit under test (methods called, arguments, HTTP projection, status codes) rather than re-asserting payload fields a mock was hardcoded to return.
- **[no-self-asserting-constants]** Assert output produced by the code under test, never a hardcoded constant, alias, or local reassignment compared against itself.
- **[no-unproven-indirect-assertions]** Verify leak or security guarantees directly on the output, or confirm that injecting the leak causes an indirect spy assertion to fail.
- **[test-live-export-not-leftover]** Import and test the live exported component or module used by production; remove specs that only exercise an unused leftover duplicate.
- **[test-canonical-urls]** Assert canonical production URLs in tests rather than legacy or alternate paths that only pass through redirects.
- **[test-unauthenticated-when-middleware-allows]** Keep unauthenticated-path tests when the route's middleware does not reject missing sessions rather than assuming every endpoint is auth-gated identically.

## 2. Style & conventions (`[style]`)

Check these after Pass 1. Align the spec to these patterns without crowding out `[issue]` findings.

- **[accessible-query-priority]** Query elements from most to least accessible (`getByRole` with name first, `getByTestId` last).
- **[no-locator-type-assertions]** Use the element type provided by the query locator or matcher directly without redundant `as` casts.
- **[test-user-event]** Drive user interactions with `user-event`, using `fireEvent` only when `user-event` cannot simulate the event.
- **[separate-queries-from-assertions]** Assign `screen.getBy...` results to variables before passing them into `expect(...)` calls.
- **[test-aaa-pattern]** Structure unit tests into clear Arrange, Act, and Assert phases with setup variables kept separate from execution and expectations.
- **[behavior-not-implementation]** Assert user-visible behavior and public contract outputs rather than internal implementation details.
- **[assert-mock-presence-or-transformed-props]** When a child component is mocked, assert that the mock rendered or received a transformed prop from the real logic under test, not behavior defined inside the mock itself.
- **[no-css-class-assertions]** Verify visual states through accessible attributes or user-visible behavior in unit tests rather than asserting CSS class names or inline styles; drop the case if it is purely visual.
- **[test-realistic-fixtures]** Populate fixtures with production-like values (UUID v4 strings, real enum members, plausible amounts) rather than placeholders like `'tx-123'` or `'user-1'`.
- **[reuse-shared-test-mocks]** Reuse shared suite mocks, render helpers, and explicit typed no-op stubs (`test-typed-stubs`) instead of inventing one-off mock shapes, local provider wrappers, or `never`/`unknown` shortcuts.
- **[test-real-logger-off]** Use the real logger configured with `LogLevel.OFF` and spies when asserting log behavior rather than mocking the logger interface.
- **[no-non-contract-negative-tests]** Restrict negative assertions to hard contracts and regression fixes; omit assertions that removed paths, route constants, or unchosen product options are absent.
- **[no-overlapping-method-tests]** Scope each spec to the unit under review without re-testing behavior owned by another method or already covered in a sibling spec.
- **[test-names-describe-behavior]** Name tests for the enduring product behavior (not a feature flag, plan unit, or removed condition), extract repeated test strings into local `SCREAMING_SNAKE_CASE` constants, keep comments minimal, and place new integration specs in the same folder as sibling endpoint tests (`match-sibling-test-location`).
