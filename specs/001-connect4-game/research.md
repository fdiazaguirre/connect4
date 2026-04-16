# Research: Connect 4 Game

**Branch**: `001-connect4-game` | **Date**: 2026-04-16

## R1: Win Detection Algorithm

**Decision**: Direction-vector scan from last placed piece.

**Rationale**: After each drop, only the last piece can create a new 4-in-a-row. Check 4 directions (horizontal, vertical, diag-ascending, diag-descending) by counting consecutive same-color pieces outward in both directions from the placed piece. O(1) per move (max 4 directions × 6 steps each = 24 checks). No need to scan entire board.

**Alternatives considered**:
- Full board scan after each move — correct but O(n×m) per move, wasteful.
- Bitboard approach — fast but adds unnecessary complexity for a 7×6 grid with JS.

## R2: Animation Approach (CSS vs JS)

**Decision**: Pure CSS `@keyframes` + class toggling from JS.

**Rationale**: CSS animations run on compositor thread (GPU-accelerated for `transform` and `opacity`). Keeps main thread free for input handling. No JS animation loop required. Simpler code. Constitution Principle II (60fps) met natively.

**Alternatives considered**:
- `requestAnimationFrame` loop — more control, but adds complexity, risk of jank if main thread busy.
- Web Animations API — good but less browser support for complex sequences; CSS keyframes are sufficient here.
- Canvas-based rendering — more powerful for effects, but loses DOM accessibility and adds significant complexity for a simple grid game.

## R3: Testing Framework — Unit

**Decision**: Vitest

**Rationale**: User specified unit testing. Vitest runs ES module code natively (no transpilation), fast, supports `import`/`export` directly. `game.js` as a pure module with no DOM makes Vitest ideal. No need for jsdom since logic is DOM-free.

**Alternatives considered**:
- Jest — heavier, requires transform config for ES modules.
- Node built-in test runner — fewer features, no coverage tooling.

## R4: Testing Framework — BDD / E2e

**Decision**: Playwright

**Rationale**: User explicitly specified Playwright for BDD. Playwright launches real browsers, supports all acceptance scenarios from spec. Built-in assertions, auto-waiting, screenshot on failure. Spec acceptance scenarios map 1:1 to Playwright `test()` blocks.

**Alternatives considered**: None — user requirement.

## R5: Project Serving for Tests

**Decision**: Use Playwright's built-in `webServer` config to serve static files during test runs.

**Rationale**: No production build step needed. Playwright config can start a simple static server (e.g., `npx serve src` or `python3 -m http.server`) before tests run and tear it down after. Zero additional infrastructure.

**Alternatives considered**:
- Vite dev server — adds a dependency for a build tool we don't need in production.
- Manual server start — error-prone, not CI-friendly.

## R6: Responsive Layout

**Decision**: CSS Grid for the board, `clamp()` / `vmin` units for sizing.

**Rationale**: CSS Grid natively represents a 7×6 grid. `vmin` or `clamp()` scales the board to fit any viewport (desktop to 320px mobile) without media query breakpoints. Constitution Principle III (playability) — touch targets sized appropriately on mobile.

**Alternatives considered**:
- Flexbox — works but requires nested containers for rows; Grid is more natural for 2D layout.
- Fixed pixel sizes with media queries — fragile, more CSS to maintain.
