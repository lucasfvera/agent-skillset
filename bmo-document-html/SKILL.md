---
name: bmo-document-html
description: Produces long-form technical documentation as a self-contained HTML page (semantic structure, readable typography, light/dark CSS) with a graphics-first bias—inline SVG, Mermaid, or styled layout for data flows, user journeys, service communication, and before/after topologies—instead of Markdown when clarity and presentation matter. Use when the user asks for architecture write-ups, handoff docs, migration notes, ADR-style narratives, or “document this” as a durable artifact; when they invoke bmo-document-html or /bmo-document-html; or when they want HTML over .md for sharing, printing, or richer layout without a doc site build step.
disable-model-invocation: true
---

# BMO document (HTML)

## Purpose

Deliver **technically rigorous** documentation as **one primary HTML file** (embedded CSS; optional JS for diagrams or small interactions). **Bias toward graphics:** humans digest **diagrams and structured layouts** faster than walls of text for anything multi-step, multi-actor, or spatial (services, queues, APIs, screens). Prefer this over Markdown when the outcome benefits from **controlled reading measure**, **hierarchy + navigation**, **visual + tabular explanation**, **theme-aware styling**, and **stable presentation** outside a renderer’s flavor-of-the-week MD extensions.

Rationale in depth (information density, sharing, interaction, tradeoffs) is summarized with sources at the top of [reference.md](reference.md).

Do **not** replace repo-required Markdown (e.g. mandated `README.md`) unless the user explicitly asks to add or change those files.

**Author’s caveat:** the source essay notes you often only need to ask for “an HTML file” without a skill; this skill still helps when you want **repeatable structure**, **a11y/Guidelines checks**, and **team-consistent** artifacts.

## When to choose HTML over Markdown

Use this skill when **any** of the following is true:

- The deliverable is a **standalone reference** (architecture, migration, integration contract) meant to be opened in a browser, attached to a ticket, or archived.
- The doc needs **more than headings and fences**: comparison tables, multi-column callouts, **service maps**, **data/control-flow diagrams**, **user-journey figures**, SVG illustrations, Mermaid, glossary, footnotes-style asides.
- The user wants **one file** with predictable appearance (no “GitHub vs VS Code vs Slack” MD divergence).
- The user names **`bmo-document-html`**, **`/bmo-document-html`**, or language like “HTML doc”, “styled write-up”, “not markdown”.

For **short** answers in chat, plain Markdown or prose in the reply is enough—do not spawn an HTML artifact.

## Operating rules

1. **Single coherent file first** — Default: `docs/<topic-slug>.html` at repo root or path the user gives. Self-contained `<style>`; add `<script type="module">` only when needed (e.g. Mermaid).
2. **Technical rigor** — Accurate paths, queue names, types, and behavior; cite code with `` `path/to/file` `` and line ranges when pointing at the repo. Distinguish “current behavior” from “removed/legacy”.
3. **Graphics-first (default)** — For any topic with **2+ actors** (services, users, queues, DBs), **non-linear control flow**, or **migration / before-after**, include at least **one primary diagram** (inline SVG, Mermaid, or a small **HTML/CSS “card + arrow” topology**). Typical shapes: **service / queue communication**; **data or request flow**; **user journey** (steps + branches); **state machine**; **layered architecture**. Wrap each in `<figure>` + `<figcaption>` that states what the reader should **take away**; add a **short legend** or numbered callouts when symbols need decoding. Prefer **vector** (SVG, Mermaid) over long prose; use `<img>` only when assets exist or are essential—always `width`, `height`, and meaningful `alt`. Patterns and diagram-type picks: [reference.md](reference.md#diagram-playbook).
4. **Readable and scannable** — Table of contents (`<nav aria-label="Table of contents">`), `<main id="main">`, sections with stable `id`s, **skip link** to main, **heading order** `h1` → `h2` → `h3`.
5. **Inclusive layout** — `color-scheme: light dark`; `prefers-reduced-motion` for `scroll-behavior` and any motion; **`:focus-visible`** on links; **meaningful `meta name="description"`**; diagrams: `role="img"`, `aria-label` or `<title>` inside SVG.
6. **Figures** — Use `<figure>` / `<figcaption>` for diagrams; `<table>` with `<th scope="col">` for contracts.
7. **Identifiers** — Wrap code tokens and hostnames with `translate="no"` where auto-translation would garble them.
8. **External JS** — If using Mermaid (or similar), load from a **versioned CDN URL**, `securityLevel: "strict"`, `startOnLoad: false` then `await mermaid.run({ querySelector: ".mermaid" })` after `initialize`. Note that **`file://` may block CDN**; mention “serve locally or use https” in a small aside.
9. **Two-way / exploratory artifacts** — When the user wants sliders, bucketing UI, or live previews, end with an explicit **export affordance** (“Copy as JSON”, “Copy as prompt”, “Copy diff”) so the browser session feeds back into the editor or Claude, per the playgrounds pattern in [reference.md](reference.md#two-way-interaction-and-playgrounds).
10. **Web Interface Guidelines** — Before finalizing UI polish on the page itself, fetch current rules from `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md` and fix obvious violations (focus, motion, semantics). See [reference.md](reference.md#web-interface-guidelines).

## Document skeleton (minimal)

- `<!DOCTYPE html>`, `<html lang="en">` (or appropriate `lang`).
- `<head>`: charset, viewport, title, meta description.
- `<body>`: skip link → `<header>` (title + lede) → `<main>`: optional `<nav class="toc">` → `<article>` with `<section id="...">` (each major concept: consider **figure + short prose**, not prose alone).
- CSS variables for `--bg`, `--surface`, `--text`, `--muted`, `--border`, `--accent`; `max-width` on `main`/`header` (~52rem); `line-height` ~1.6; `pre`/`code` styles.
- Footer or `<aside>` for “related links”, changelog, or self-audit.

Fuller rationale, HTML-vs-Md notes, **diagram playbook**, and source article: [reference.md](reference.md).

## Verification

- Open the file in a browser (or `python -m http.server` from parent) and confirm layout, TOC anchors, and **every diagram** (Mermaid/SVG/CSS layout) renders.
- For flow-, architecture-, or migration-shaped docs, confirm there is at least **one** clear visual for the hardest concept (not only tables of text).
- Run `read_lints` only if the repo tracks HTML; otherwise quick manual pass: keyboard tab to skip link and first in-doc link.

## Anti-patterns

- Dumping the entire chat into HTML with no structure.
- **Walls of text** where a **single diagram** (flow, sequence, topology) would carry the same truth faster—especially for integrations, auth paths, or multi-service calls.
- Markdown-with-HTML-tags hybrid as the **only** artifact when the user asked for a proper HTML doc.
- Inline `<script>` with non-versioned CDN `latest` URLs for reproducibility.
- Diagrams without text alternative for screen readers.
- Decorative graphics with **no stated takeaway** in the caption—every figure should answer “what should I believe after looking at this?”
