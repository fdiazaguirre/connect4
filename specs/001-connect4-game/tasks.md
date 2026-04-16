---
description: "Task list for Connect 4 Game implementation"
---

# Tasks: Connect 4 Game

**Input**: Design documents from `specs/001-connect4-game/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, research.md ✅, quickstart.md ✅

**Tests**: Included — unit tests (Vitest) and BDD e2e tests (Playwright) requested in user input.

**Organization**: Tasks grouped by user story for independent implementation and testing. Three parallel tracks run throughout: CSS, game logic, and test writing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US4)
- Exact file paths in all descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization. T002–T004 run in parallel after T001.

- [ ] T001 Create directory structure: `src/`, `src/css/`, `src/js/`, `tests/unit/`, `tests/e2e/`
- [ ] T002 [P] Create `package.json` with devDependencies: `vitest`, `@vitest/coverage-v8`, `playwright`, `@playwright/test`, `serve`; scripts: `test`, `test:coverage`, `test:watch`, `test:e2e`
- [ ] T003 [P] Create `vitest.config.js` targeting `tests/unit/**`, environment `node`, coverage via `@vitest/coverage-v8`
- [ ] T004 [P] Create `playwright.config.js` with `testDir: 'tests/e2e'`, `webServer` serving `src/` via `npx serve`, baseURL `http://localhost:3000`

---

## Phase 2: Foundational

**Purpose**: HTML skeleton, CSS shell, and JS module stubs — blocking all user stories.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.

- [ ] T005 Create `src/index.html`: semantic structure with `<div id="board">`, `<div id="status">`, `<button id="reset-btn">New Game</button>`, and `<script type="module" src="js/app.js">` import
- [ ] T006 [P] Create `src/css/styles.css`: CSS Grid board (`grid-template-columns: repeat(7, 1fr)`, `grid-template-rows: repeat(6, 1fr)`), CSS variables (`--p1-color`, `--p2-color`, `--cell-size` via `clamp()`/`vmin`), responsive scaling to 320px, `@media (prefers-reduced-motion: reduce)` override setting all animation durations to `0ms`
- [ ] T007 [P] Create `src/js/game.js`: stub exports for all 6 functions from data-model.md (`createGame`, `dropPiece`, `checkWin`, `checkDraw`, `resetGame`, `isValidDrop`) — each returning `null` with correct JSDoc signatures
- [ ] T008 [P] Create `src/js/renderer.js`: stub exports for `renderBoard(state)`, `animateDrop(row, col, callback)`, `highlightWin(cells)`, `showStatus(state)`, `clearHighlights()`
- [ ] T009 [P] Create `src/js/app.js`: `DOMContentLoaded` listener, `import` from `game.js` and `renderer.js`, initialize game state via `createGame()`, call `renderBoard(state)`

**Checkpoint**: Static page loads in browser with empty board grid, status area, and reset button visible.

---

## Phase 3: User Story 1 — Drop Piece Into Column (Priority: P1) 🎯 MVP

**Goal**: Two players alternate clicking columns; pieces drop to lowest available row; turn switches; full columns rejected.

**Independent Test**: Open game in browser, click any column, verify piece appears in bottom row, turn indicator flips, full column shows no change.

### Parallel Batch A — Logic + Tests + CSS (run all simultaneously)

- [ ] T010 [P] [US1] Implement `createGame()` returning full `GameState` initial state (`board` 6×7 zeros, `currentPlayer: 1`, `status: 'playing'`, `winner: null`, `winningCells: []`, `moveCount: 0`) in `src/js/game.js`
- [ ] T011 [P] [US1] Implement `isValidDrop(board, col)` — returns `false` when `board[0][col] !== 0` or `col` out of range — in `src/js/game.js`
- [ ] T012 [P] [US1] Write FAILING Vitest unit tests for US1 in `tests/unit/game.test.js`: board initialization shape, `isValidDrop` on empty/partial/full columns, `dropPiece` gravity (piece lands at lowest empty row), turn switching (1→2→1), `moveCount` increment, full-column no-op
- [ ] T013 [P] [US1] Implement drop animation `@keyframes drop-piece` (translate from column top to target row via `translateY`) and column hover highlight (`:hover` glow + preview indicator) in `src/css/styles.css`

### Sequential — after T010 and T011

- [ ] T014 [US1] Implement `dropPiece(state, col)`: call `isValidDrop`, find lowest empty row (scan `row=5` down to `0`), return new state with piece placed, `moveCount` incremented, `currentPlayer` switched; return `{ state, row: -1 }` if invalid — in `src/js/game.js`

### Sequential — after T014 and T013

- [ ] T015 [US1] Implement `renderBoard(state)`: build 42 `<div class="cell">` elements with `data-row` / `data-col` attributes and player class (`player-1` / `player-2`), replace `#board` contents — in `src/js/renderer.js`
- [ ] T016 [US1] Implement `animateDrop(row, col, callback)`: add `.drop-active` class to target cell, invoke `callback` after `animationend` event (or immediately if `prefers-reduced-motion`) — in `src/js/renderer.js`
- [ ] T017 [US1] Implement `showStatus(state)`: update `#status` text to "Player X's turn" / "Player X wins!" / "Draw!" based on `state.status` and `state.currentPlayer` — in `src/js/renderer.js`

### Sequential — after T015, T016, T017

- [ ] T018 [US1] Wire column click in `src/js/app.js`: event delegation on `#board` cells → derive `col` from `data-col` → call `dropPiece` → `animateDrop` → `renderBoard` + `showStatus`; block clicks when `state.status !== 'playing'`
- [ ] T019 [US1] Write Playwright BDD tests for US1 in `tests/e2e/connect4.spec.js`: click column on empty board → piece in row 5, status shows Player 2; click column with 3 pieces → piece in row 2; click full column → no state change

**Checkpoint**: US1 independently testable — drop pieces, see gravity and turn switch, full column rejected.

---

## Phase 4: User Story 2 — Win Detection and Announcement (Priority: P2)

**Goal**: After each drop, detect 4-in-a-row in all 4 directions; highlight winning cells; announce winner; block further moves.

**Independent Test**: Drop 3 same-color pieces then the 4th; verify win banner + 4-cell highlight appear; verify clicking any column does nothing.

### Parallel Batch B — Logic + Tests + CSS (run all simultaneously)

- [ ] T020 [P] [US2] Implement `checkWin(board, row, col)` using direction-vector scan (per research.md R1): 4 directions `[0,1]`, `[1,0]`, `[1,1]`, `[1,-1]`; count consecutive same-player cells in both directions; return array of 4 `[row,col]` winning coordinates or `null` — in `src/js/game.js`
- [ ] T021 [P] [US2] Write FAILING Vitest unit tests for `checkWin` in `tests/unit/game.test.js`: horizontal win row 5 cols 0–3, vertical win col 3 rows 2–5, diagonal-ascending win, diagonal-descending win, near-miss (3 in a row), edge positions (corners, borders), no false positive on interleaved pieces
- [ ] T022 [P] [US2] Implement win styles in `src/css/styles.css`: `.winning-cell` glow animation (`box-shadow` pulse `@keyframes`), `#winner-banner` overlay with fade-in, Player 1 / Player 2 color variants

### Sequential — after T020

- [ ] T023 [US2] Integrate `checkWin` into `dropPiece` flow: after placing piece call `checkWin(board, row, col)`; if result non-null update `state.status = 'won'`, `state.winner = currentPlayer`, `state.winningCells = result`; skip turn switch — in `src/js/game.js`

### Sequential — after T022

- [ ] T024 [US2] Implement `highlightWin(cells)`: add `.winning-cell` class to each `[row,col]` cell element in `src/js/renderer.js`

### Sequential — after T023 and T024

- [ ] T025 [US2] Update `src/js/app.js`: when `state.status === 'won'` call `highlightWin(state.winningCells)` and `showStatus(state)`; move-blocking already handled by T018 guard
- [ ] T026 [US2] Add Playwright BDD tests for US2 in `tests/e2e/connect4.spec.js`: horizontal win triggers banner + 4 cells highlighted; vertical win detected; diagonal win detected; post-win column click is no-op

**Checkpoint**: US1 + US2 independently functional — play to a win, see highlight + announcement.

---

## Phase 5: User Story 3 — Draw Detection (Priority: P3)

**Goal**: When all 42 cells filled with no winner, show draw message and block further moves.

**Independent Test**: Programmatically fill board with no win pattern; verify draw message appears on 42nd piece.

### Parallel Batch C — Logic + Tests + CSS (run all simultaneously)

- [ ] T027 [P] [US3] Implement `checkDraw(state)`: return `true` when `state.moveCount === 42` and `state.status !== 'won'` — in `src/js/game.js`
- [ ] T028 [P] [US3] Write FAILING Vitest unit tests for `checkDraw` in `tests/unit/game.test.js`: returns `false` at move 41, returns `true` at move 42 with `status !== 'won'`, returns `false` if won at move 42
- [ ] T029 [P] [US3] Implement draw banner styles in `src/css/styles.css`: `.draw-banner` neutral color (distinct from win banners)

### Sequential — after T027

- [ ] T030 [US3] Integrate `checkDraw` into `dropPiece` flow (after win check): if `checkDraw(state)` set `state.status = 'draw'` — in `src/js/game.js`

### Sequential — after T030 and T029

- [ ] T031 [US3] Update `src/js/app.js`: when `state.status === 'draw'` call `showStatus(state)` (draw message already in renderer T017); move-blocking handled by existing guard
- [ ] T032 [US3] Add Playwright BDD test for US3 in `tests/e2e/connect4.spec.js`: simulate full board via scripted moves; verify draw message on 42nd piece; verify no further moves accepted

**Checkpoint**: US1 + US2 + US3 functional — games end correctly in win or draw.

---

## Phase 6: User Story 4 — New Game Reset (Priority: P4)

**Goal**: "New Game" button resets board to empty, Player 1 active, from any game state.

**Independent Test**: After a win, click New Game; verify empty board and Player 1 indicator.

### Parallel Batch D — Logic + Tests + CSS (run all simultaneously)

- [ ] T033 [P] [US4] Implement `resetGame()` returning `createGame()` initial state — in `src/js/game.js`
- [ ] T034 [P] [US4] Write FAILING Vitest unit tests for `resetGame` in `tests/unit/game.test.js`: returns clean board, `currentPlayer: 1`, `status: 'playing'`, `moveCount: 0`, `winningCells: []`
- [ ] T035 [P] [US4] Add reset button hover/active/focus styles to `src/css/styles.css`: visible focus ring for accessibility

### Sequential — after T033

- [ ] T036 [US4] Wire `#reset-btn` click in `src/js/app.js`: `resetGame()` → `clearHighlights()` → `renderBoard(state)` → `showStatus(state)`
- [ ] T037 [US4] Add Playwright BDD tests for US4 in `tests/e2e/connect4.spec.js`: reset during play → empty board + Player 1; reset after win → clears highlight + empty board; reset after draw → empty board

**Checkpoint**: All 4 user stories independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T038 [P] Run `npm test` — verify all Vitest unit tests pass (0 failures)
- [ ] T039 [P] Run `npm run test:e2e` — verify all Playwright BDD scenarios pass (0 failures)
- [ ] T040 [P] Verify `prefers-reduced-motion`: open browser with OS reduced-motion enabled, confirm piece drops and win animations are instant (0ms)
- [ ] T041 [P] Verify responsive layout: resize browser to 320px width, confirm board remains playable and touch targets are ≥44px
- [ ] T042 Run complete game playthrough per `specs/001-connect4-game/quickstart.md`: win via horizontal, win via diagonal, draw, reset — validate all success criteria SC-001 through SC-005

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T002–T004 run in parallel after T001
- **Foundational (Phase 2)**: Depends on Phase 1 — T006–T009 all run in parallel; BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — T010–T013 first parallel batch, then sequential T014–T019
- **US2 (Phase 4)**: Depends on US1 completion (T018) — T020–T022 parallel, then T023–T026 sequential
- **US3 (Phase 5)**: Depends on US2 completion (T025) — T027–T029 parallel, then T030–T032 sequential
- **US4 (Phase 6)**: Depends on US3 completion (T031) — T033–T035 parallel, then T036–T037 sequential
- **Polish (Phase 7)**: Depends on all user stories complete — T038–T041 run in parallel, T042 last

### Within Each User Story

- Tests (T012, T021, T028, T034) written in parallel with logic implementation — fail first, pass after implementation
- CSS tasks (T013, T022, T029, T035) always parallel with logic
- DOM wiring tasks always last within a story (depend on logic + renderer)

---

## Parallel Execution Examples

### Phase 3 Batch A (4 simultaneous tasks)

```bash
# All start at same time — independent files:
Task T010: "Implement createGame() in src/js/game.js"
Task T011: "Implement isValidDrop() in src/js/game.js"
Task T012: "Write failing Vitest unit tests in tests/unit/game.test.js"
Task T013: "Implement drop animation CSS in src/css/styles.css"
```

### Phase 4 Batch B (3 simultaneous tasks)

```bash
Task T020: "Implement checkWin() in src/js/game.js"
Task T021: "Write failing Vitest tests for checkWin in tests/unit/game.test.js"
Task T022: "Implement win highlight CSS in src/css/styles.css"
```

### Phase 7 (4 simultaneous validations)

```bash
Task T038: "npm test"
Task T039: "npm run test:e2e"
Task T040: "prefers-reduced-motion verification"
Task T041: "320px responsive layout verification"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T009)
3. Complete Phase 3: US1 — Drop Piece (T010–T019)
4. **STOP and VALIDATE**: Click columns, verify gravity and turn switch
5. Deploy/demo if ready

### Incremental Delivery

1. Foundation → US1 (drop pieces) → demo interactive board
2. Add US2 (win detection) → demo complete win flow
3. Add US3 (draw detection) → demo all end states
4. Add US4 (reset) → demo full replayable game
5. Polish → production-ready

---

## Notes

- `[P]` tasks operate on different files or are pure reads — safe to parallelize
- Tests marked `[P]` are written to FAIL first (TDD); they pass after their corresponding logic task completes
- `game.js` pure functions have no DOM dependency — unit tests run in Node (no browser)
- Playwright e2e tests require the static server (`npx serve src`) started by playwright.config.js `webServer`
- Win detection uses direction-vector scan per research.md R1 (not full board scan)
- CSS animation duration variables must be `0ms` under `prefers-reduced-motion` (Principle IV)
