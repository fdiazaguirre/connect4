# Implementation Plan: Connect 4 Game

**Branch**: `001-connect4-game` | **Date**: 2026-04-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-connect4-game/spec.md`

## Summary

Browser-based Connect 4 game for two local players on a 7×6 grid with gravity-based piece placement, 4-direction win detection, draw detection, and visual effects. Built with plain HTML/CSS/JS — no frameworks. Quality gates via Vitest (unit) and Playwright (BDD/e2e).

## Technical Context

**Language/Version**: HTML5, CSS3, JavaScript ES2022+
**Primary Dependencies**: None (vanilla); Vitest (unit tests), Playwright (e2e/BDD)
**Storage**: N/A (in-memory game state only)
**Testing**: Vitest (unit tests for game logic), Playwright (BDD acceptance scenarios)
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge — last 2 versions)
**Project Type**: Static web application (single page, no build step for production)
**Performance Goals**: 60 fps animations, <100ms input-to-render for piece placement
**Constraints**: No runtime dependencies, no build step for game code, responsive down to 320px viewport width
**Scale/Scope**: Single page, ~4 source files, 2 test suites

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Correctness First | Game logic in pure JS module, independently testable. Win detection covers all 4 directions. Vitest unit tests cover all board states. | ✅ PASS |
| II. Responsive UI | CSS animations via `transform`/`opacity` (GPU-composited). Non-blocking: animations are fire-and-forget, input handler doesn't `await` them. 60fps target. | ✅ PASS |
| III. Playability | Turn indicator, column hover preview, win highlight, reset button — all discoverable without instructions. | ✅ PASS |
| IV. Visual Engagement | Drop animation, win glow, hover preview. All additive. `prefers-reduced-motion` media query disables animations. | ✅ PASS |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/001-connect4-game/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
src/
├── index.html           # Single page — board, status bar, reset button
├── css/
│   └── styles.css       # Grid layout, piece colors, animations, responsive, reduced-motion
└── js/
    ├── game.js          # Pure logic: board state, dropPiece, checkWin, checkDraw, reset
    ├── renderer.js      # DOM updates: renderBoard, animateDrop, highlightWin, showStatus
    └── app.js           # Entry point: event listeners, game↔renderer wiring

tests/
├── unit/
│   └── game.test.js     # Vitest: board init, drop logic, win detection (all directions), draw, reset, edge cases
└── e2e/
    └── connect4.spec.js # Playwright BDD: acceptance scenarios from spec (US1–US4)

package.json             # Dev dependencies: vitest, playwright
vitest.config.js         # Vitest config
playwright.config.js     # Playwright config
```

**Structure Decision**: Single-project flat layout. No frontend/backend split — pure client-side app. Game logic separated from rendering for testability (Principle I). `game.js` exports pure functions; `renderer.js` handles DOM; `app.js` wires them.

## Architecture Decisions

### Separation: Logic vs. Rendering

`game.js` is a pure state module — no DOM access. It exports functions like `createBoard()`, `dropPiece(board, col, player)`, `checkWin(board, lastRow, lastCol)`, `checkDraw(board)`, `resetGame()`. Returns new state or result objects. This enables Vitest unit tests without any DOM mocking.

`renderer.js` reads game state and updates the DOM. It does NOT mutate game state. One-way data flow: user event → `app.js` → `game.js` (mutate state) → `renderer.js` (render).

### Animation Strategy

CSS `@keyframes` for piece drop (translate Y from top of column to target row). CSS transitions for hover glow and win highlight. JS only triggers animations by adding CSS classes; never uses `requestAnimationFrame` loops for game rendering.

`prefers-reduced-motion: reduce` → all animation durations set to 0ms via media query override.

### Testing Strategy

**Unit (Vitest)**: Test `game.js` functions in isolation. Board state in, result out. No DOM, no browser. Covers: board initialization, valid/invalid drops, all 4 win directions at every possible board position, draw detection, full-column rejection, reset.

**BDD/E2e (Playwright)**: Test acceptance scenarios from spec. Launches browser, interacts with actual page. Covers: US1 (drop piece, turn switch, full column), US2 (win all directions, post-win block), US3 (draw detection), US4 (reset from all states). Uses `page.click()` on columns, asserts DOM state.

### No Build Step

Production game code runs directly in browser via `<script type="module">`. No bundler, no transpiler. `package.json` only holds dev dependencies (vitest, playwright, `@vitest/coverage-v8`). Dev server for Playwright via `npx playwright` or simple static server.

## Complexity Tracking

> No violations to justify. All decisions align with constitution.
