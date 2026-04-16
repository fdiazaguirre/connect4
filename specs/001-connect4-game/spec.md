# Feature Specification: Connect 4 Game

**Feature Branch**: `001-connect4-game`
**Created**: 2026-04-16
**Status**: Draft
**Input**: User description: "Connect4 is a game where two players take turns dropping pieces into a 7x6 grid. The first player to place 4 tokens in a row horizontally, vertically or diagonally wins. The players always insert a token in a column, and the token drops to the lowest available space."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Drop Piece Into Column (Priority: P1)

Two players alternate turns. On each turn, the active player selects a column (1–7). A piece in that player's color drops to the lowest unoccupied row in that column. The turn then passes to the other player.

**Why this priority**: Core mechanic without which no other story can function. Delivers a minimal interactive board.

**Independent Test**: Open game, click any column, verify piece appears in correct lowest row, verify turn indicator switches to other player.

**Acceptance Scenarios**:

1. **Given** an empty board, **When** Player 1 clicks column 4, **Then** a Player 1 piece appears in row 6 (bottom) of column 4 and the turn indicator shows Player 2.
2. **Given** column 4 has 3 pieces, **When** Player 1 clicks column 4, **Then** a Player 1 piece appears in row 3 (next available from bottom) of column 4.
3. **Given** a column is full (6 pieces), **When** any player clicks that column, **Then** no piece is placed and no turn change occurs; the column is visually indicated as unavailable.

---

### User Story 2 - Win Detection and Announcement (Priority: P2)

After every piece placement, the game evaluates all four win directions (horizontal, vertical, diagonal ascending, diagonal descending). If a player has 4 consecutive pieces in any direction, the game immediately ends, highlights the winning four pieces, and announces the winner.

**Why this priority**: Without win detection the game has no end state, removing its core purpose.

**Independent Test**: Manually place 3 same-color pieces in a row, then drop the 4th; verify win announcement and highlight appear. Repeat for all 4 directions.

**Acceptance Scenarios**:

1. **Given** Player 1 has 3 horizontal pieces in row 6 columns 1–3, **When** Player 1 drops in column 4, **Then** the 4 pieces glow/highlight and a banner declares Player 1 the winner; no further moves are accepted.
2. **Given** Player 2 has 3 vertical pieces in column 5 rows 6–4, **When** Player 2 drops in column 5, **Then** win is detected vertically and declared for Player 2.
3. **Given** Player 1 has 3 diagonal pieces, **When** Player 1 places the 4th, **Then** win is detected diagonally for that direction.
4. **Given** a win has been declared, **When** any player clicks a column, **Then** no new piece is placed.

---

### User Story 3 - Draw Detection (Priority: P3)

When all 42 cells are occupied and no player has won, the game ends in a draw and displays a draw message.

**Why this priority**: Completes the end-state coverage; without it, a full board can cause undefined behavior.

**Independent Test**: Fill all cells without triggering a win; verify draw message appears.

**Acceptance Scenarios**:

1. **Given** the board has 41 pieces with no winner, **When** the last piece is placed, **Then** a draw message is displayed immediately and no further moves are accepted.
2. **Given** a draw is declared, **When** any player clicks a column, **Then** nothing happens.

---

### User Story 4 - New Game Reset (Priority: P4)

At any point (mid-game, post-win, post-draw), a player can trigger a reset. All cells clear, turn order returns to Player 1, and the board is ready for a new game.

**Why this priority**: Essential for replayability; game is unusable long-term without it.

**Independent Test**: After a win, click Reset; verify board is empty, Player 1 is active.

**Acceptance Scenarios**:

1. **Given** a game is in progress, **When** "New Game" is clicked, **Then** the board resets to empty and Player 1's turn is active.
2. **Given** a completed game (win or draw), **When** "New Game" is clicked, **Then** the board resets to empty and Player 1's turn begins.

---

### Edge Cases

- What happens when a player rapidly double-clicks the same column? (Only one piece must be placed per turn.)
- How does the game handle simultaneous win and full-board conditions? (Win takes precedence over draw.)
- Can both players have 4-in-a-row from the same final move? (Not possible in Connect 4 — only the active player places a piece, so only their win is checked.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Game MUST display a 7-column × 6-row grid.
- **FR-002**: Game MUST alternate turns between two players starting with Player 1.
- **FR-003**: Game MUST drop a piece to the lowest available row in the selected column.
- **FR-004**: Game MUST prevent placement in a full column and provide visual feedback.
- **FR-005**: Game MUST detect 4-in-a-row horizontally, vertically, and in both diagonals after each move.
- **FR-006**: Game MUST highlight the 4 winning pieces upon win detection.
- **FR-007**: Game MUST display a clear winner or draw announcement when the game ends.
- **FR-008**: Game MUST prevent further moves after a game-ending state (win or draw).
- **FR-009**: Game MUST provide a "New Game" reset action available at any game state.
- **FR-010**: Game MUST visually distinguish Player 1's pieces from Player 2's pieces at all times.
- **FR-011**: Game MUST clearly indicate whose turn it is.
- **FR-012**: Hovering over a column MUST provide visual feedback indicating where the piece will land.

### Key Entities

- **Board**: 7 × 6 grid of cells, each empty or occupied by Player 1 or Player 2.
- **Piece**: A token belonging to one player, placed in a specific cell.
- **Turn**: The current active player (Player 1 or Player 2).
- **GameState**: One of `playing`, `won` (with winner + winning cells), `draw`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A complete game (from start through win or draw) can be played without any bugs, invalid states, or crashes.
- **SC-002**: Piece placement, including gravity and win-check, resolves and renders within 100ms of user input.
- **SC-003**: Win detection correctly identifies all four directions across 100% of possible winning positions on a 7×6 board.
- **SC-004**: First-time players can understand and play the game without any written instructions, solely from visual cues.
- **SC-005**: Animated piece drop and win highlight do not delay the next player's input by more than one animation cycle.

## Assumptions

- Two human players sharing the same screen (local multiplayer); no AI opponent in scope.
- No persistent scoring, accounts, or match history required.
- Mobile support is in scope (web game must be responsive), but keyboard-only navigation is not required for v1.
- Player 1 is always the first to move at game start and after each reset.
- No network or multiplayer over the internet required.
