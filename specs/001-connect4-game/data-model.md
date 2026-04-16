# Data Model: Connect 4 Game

**Branch**: `001-connect4-game` | **Date**: 2026-04-16

## Entities

### Board

A 2D array: `board[row][col]` where `row=0` is top, `row=5` is bottom. 7 columns × 6 rows.

| Field | Type | Description |
|-------|------|-------------|
| cells | `number[][]` | 6×7 matrix. `0` = empty, `1` = Player 1, `2` = Player 2 |

### GameState

| Field | Type | Description |
|-------|------|-------------|
| board | `Board` | Current board |
| currentPlayer | `1 \| 2` | Whose turn it is |
| status | `'playing' \| 'won' \| 'draw'` | Game phase |
| winner | `1 \| 2 \| null` | Set when status = 'won' |
| winningCells | `[row, col][]` | Array of 4 cell coordinates forming the win line |
| moveCount | `number` | Total pieces placed (0–42). Draw when 42 and no winner. |

### State Transitions

```
INITIAL (createGame)
  → status: 'playing', currentPlayer: 1, moveCount: 0, board: all zeros

PLAYING (dropPiece)
  → on valid drop: place piece, increment moveCount, check win
    → if win detected: status: 'won', winner: currentPlayer, winningCells: [4 coords]
    → if moveCount == 42: status: 'draw'
    → else: switch currentPlayer (1↔2)
  → on invalid drop (column full): no state change

WON / DRAW (terminal)
  → dropPiece is no-op
  → resetGame → returns to INITIAL
```

## Function Signatures (game.js)

| Function | Input | Output | Side Effect |
|----------|-------|--------|-------------|
| `createGame()` | — | `GameState` | None |
| `dropPiece(state, col)` | `GameState`, column `0–6` | `{ state: GameState, row: number \| -1 }` | None (returns new state) |
| `checkWin(board, row, col)` | board, last placed row/col | `[row,col][] \| null` | None |
| `checkDraw(state)` | `GameState` | `boolean` | None |
| `resetGame()` | — | `GameState` | None (same as createGame) |
| `isValidDrop(board, col)` | board, column | `boolean` | None |

All functions are pure — no mutations, no DOM access.
