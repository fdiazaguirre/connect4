import { createGame, dropPiece, resetGame } from './game.js';
import { renderBoard, showStatus, animateDrop, highlightWin, clearHighlights } from './renderer.js';

let state = createGame();

document.addEventListener('DOMContentLoaded', () => {
  renderBoard(state);
  showStatus(state);

  const board = document.querySelector('#board');

  // Column click — drop a piece
  board.addEventListener('click', (event) => {
    const cell = event.target.closest('.cell');
    if (!cell) return;

    const col = parseInt(cell.dataset.col);

    if (state.status !== 'playing') return;

    const { state: newState, row } = dropPiece(state, col);
    if (row === -1) return;

    state = newState;
    animateDrop(row, col, () => {
      renderBoard(state);
      showStatus(state);
      if (state.status === 'won') {
        highlightWin(state.winningCells);
      }
    });
  });

  // Reset button handler
  document.querySelector('#reset-btn').addEventListener('click', () => {
    state = resetGame();
    clearHighlights();
    renderBoard(state);
    showStatus(state);
  });

  // Column hover highlight — only on empty cells while game is active
  board.addEventListener('mouseover', (event) => {
    if (state.status !== 'playing') return;
    const cell = event.target.closest('.cell');
    if (!cell) return;
    const col = cell.dataset.col;
    board.querySelectorAll(`.cell[data-col="${col}"]:not(.player-1):not(.player-2)`)
      .forEach((c) => c.classList.add('col-hover'));
  });

  board.addEventListener('mouseout', (event) => {
    const cell = event.target.closest('.cell');
    if (!cell) return;
    const col = cell.dataset.col;
    board.querySelectorAll(`.cell[data-col="${col}"]`)
      .forEach((c) => c.classList.remove('col-hover'));
  });
});
