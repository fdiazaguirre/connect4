/**
 * @fileoverview DOM rendering functions for the Connect 4 game.
 * Responsible for translating GameState into visual updates and animations.
 */

/**
 * Reads the current GameState and updates the #board DOM element to reflect it.
 *
 * @param {import('./gameState.js').GameState} state - The current game state.
 * @returns {void}
 */
export function renderBoard(state) {
  const board = document.getElementById('board');
  board.innerHTML = '';
  for (let row = 0; row <= 5; row++) {
    for (let col = 0; col <= 6; col++) {
      const cell = document.createElement('div');
      cell.className = 'cell';
      cell.dataset.row = row;
      cell.dataset.col = col;
      if (state.board[row][col] === 1) {
        cell.classList.add('player-1');
      } else if (state.board[row][col] === 2) {
        cell.classList.add('player-2');
      }
      board.appendChild(cell);
    }
  }
}

/**
 * Triggers a CSS drop animation for a disc falling into the given cell,
 * then calls the provided callback once the animation has completed.
 *
 * @param {number} row - Zero-based row index of the destination cell.
 * @param {number} col - Zero-based column index of the destination cell.
 * @param {function(): void} callback - Called when the drop animation ends.
 * @returns {void}
 */
export function animateDrop(row, col, callback) {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    callback();
    return;
  }
  const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
  if (!cell) {
    callback();
    return;
  }
  cell.classList.add('drop-active');
  cell.addEventListener('animationend', () => {
    cell.classList.remove('drop-active');
    callback();
  }, { once: true });
}

/**
 * Adds the `.winning-cell` CSS class to each of the four cells that form
 * the winning combination, visually highlighting them.
 *
 * @param {Array<[number, number]>} cells - Array of exactly 4
 *   [row, col] tuples describing the winning cell positions.
 * @returns {void}
 */
export function highlightWin(cells) {
  cells.forEach(([row, col]) => {
    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    if (cell) cell.classList.add('winning-cell');
  });
}

/**
 * Updates the #status element's text content to reflect the current
 * game state (e.g. whose turn it is, or the winner).
 *
 * @param {import('./gameState.js').GameState} state - The current game state.
 * @returns {void}
 */
export function showStatus(state) {
  const el = document.getElementById('status');
  if (state.status === 'playing') {
    el.textContent = `Player ${state.currentPlayer}'s turn`;
    el.classList.remove('status-won', 'status-draw');
  } else if (state.status === 'won') {
    el.textContent = `Player ${state.winner} wins! 🎉`;
    el.classList.add('status-won');
    el.classList.remove('status-draw');
  } else if (state.status === 'draw') {
    el.textContent = "It's a draw!";
    el.classList.add('status-draw');
    el.classList.remove('status-won');
  }
}

/**
 * Removes the `.winning-cell` CSS class from every cell on the board,
 * clearing any active win highlights.
 *
 * @returns {void}
 */
export function clearHighlights() {
  document.querySelectorAll('.winning-cell').forEach(el => el.classList.remove('winning-cell'));
}
