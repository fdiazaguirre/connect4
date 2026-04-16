/**
 * Connect 4 game logic module.
 * Pure logic — no DOM access, no side effects.
 *
 * @module game
 */

/**
 * @typedef {Object} GameState
 * @property {number[][]} board - 6 rows × 7 cols grid (0=empty, 1=player1, 2=player2)
 * @property {1|2} currentPlayer - The player whose turn it is
 * @property {'playing'|'won'|'draw'} status - Current game status
 * @property {1|2|null} winner - The winning player, or null if no winner yet
 * @property {Array<[number, number]>} winningCells - Array of [row, col] pairs for the winning line
 * @property {number} moveCount - Total number of moves made so far
 */

/**
 * Creates a new game state with an empty board and default values.
 *
 * @returns {GameState} A fresh game state with a 6×7 board of zeros
 */
export function createGame() {
  return {
    board: Array.from({ length: 6 }, () => new Array(7).fill(0)),
    currentPlayer: 1,
    status: 'playing',
    winner: null,
    winningCells: [],
    moveCount: 0
  };
}

/**
 * Drops a piece for the current player into the specified column.
 *
 * @param {GameState} state - The current game state
 * @param {number} col - The 0-indexed column (0–6) to drop the piece into
 * @returns {{ state: GameState, row: number }} Updated game state and the row where the piece landed (-1 if invalid)
 */
export function dropPiece(state, col) {
  if (state.status !== 'playing') {
    return { state, row: -1 };
  }

  if (!isValidDrop(state.board, col)) {
    return { state, row: -1 };
  }

  let foundRow = -1;
  for (let row = 5; row >= 0; row--) {
    if (state.board[row][col] === 0) {
      foundRow = row;
      break;
    }
  }

  const newBoard = state.board.map(r => [...r]);
  newBoard[foundRow][col] = state.currentPlayer;

  const newMoveCount = state.moveCount + 1;

  const winResult = checkWin(newBoard, foundRow, col);
  if (winResult !== null) {
    return {
      state: {
        ...state,
        board: newBoard,
        status: 'won',
        winner: state.currentPlayer,
        winningCells: winResult,
        moveCount: newMoveCount
      },
      row: foundRow
    };
  }

  const partialState = { ...state, board: newBoard, moveCount: newMoveCount, status: 'playing' };
  if (checkDraw(partialState)) {
    return { state: { ...partialState, status: 'draw' }, row: foundRow };
  }

  return { state: { ...partialState, currentPlayer: state.currentPlayer === 1 ? 2 : 1 }, row: foundRow };
}

/**
 * Checks whether the last placed piece at (row, col) produces a winning line.
 *
 * @param {number[][]} board - The current board grid
 * @param {number} row - The row index of the last placed piece
 * @param {number} col - The column index of the last placed piece
 * @returns {Array<[number, number]>|null} Array of 4 [row, col] winning cell coordinates, or null if no win
 */
export function checkWin(board, row, col) {
  const player = board[row][col];
  const directions = [
    [0, 1],   // horizontal
    [1, 0],   // vertical
    [1, 1],   // diagonal-desc
    [1, -1],  // diagonal-asc
  ];

  for (const [dr, dc] of directions) {
    const cells = [[row, col]];

    // Count in the positive direction [dr, dc]
    for (let step = 1; step <= 3; step++) {
      const r = row + dr * step;
      const c = col + dc * step;
      if (r < 0 || r >= 6 || c < 0 || c >= 7 || board[r][c] !== player) break;
      cells.push([r, c]);
    }

    // Count in the negative direction [-dr, -dc]
    for (let step = 1; step <= 3; step++) {
      const r = row - dr * step;
      const c = col - dc * step;
      if (r < 0 || r >= 6 || c < 0 || c >= 7 || board[r][c] !== player) break;
      cells.push([r, c]);
    }

    if (cells.length >= 4) {
      return cells.slice(0, 4);
    }
  }

  return null;
}

/**
 * Checks whether the current game state is a draw (board full, no winner).
 *
 * @param {GameState} state - The current game state
 * @returns {boolean} True if the game is a draw, false otherwise
 */
export function checkDraw(state) {
  return state.moveCount === 42 && state.status !== 'won';
}

/**
 * Determines whether a piece can be dropped into the specified column.
 *
 * @param {number[][]} board - The current board grid
 * @param {number} col - The 0-indexed column (0–6) to check
 * @returns {boolean} True if the column is valid and has at least one empty cell, false otherwise
 */
export function isValidDrop(board, col) {
  return col >= 0 && col <= 6 && board[0][col] === 0;
}

/**
 * Resets the game to a fresh initial state.
 *
 * @returns {GameState} A fresh game state (same as createGame)
 */
export function resetGame() {
  return createGame();
}
