import { describe, it, expect } from 'vitest';
import { createGame, isValidDrop, dropPiece, checkWin, checkDraw, resetGame } from '../../src/js/game.js';

describe('createGame', () => {
  it('returns a 6×7 board with all zeros', () => {
    const game = createGame();
    expect(game.board).toHaveLength(6);
    game.board.forEach(row => {
      expect(row).toHaveLength(7);
      row.forEach(cell => expect(cell).toBe(0));
    });
  });

  it('sets currentPlayer to 1', () => {
    const game = createGame();
    expect(game.currentPlayer).toBe(1);
  });

  it('sets status to "playing"', () => {
    const game = createGame();
    expect(game.status).toBe('playing');
  });

  it('sets moveCount to 0', () => {
    const game = createGame();
    expect(game.moveCount).toBe(0);
  });

  it('sets winningCells to an empty array', () => {
    const game = createGame();
    expect(game.winningCells).toEqual([]);
  });
});

describe('isValidDrop', () => {
  it('returns true for all columns 0–6 on an empty board', () => {
    const { board } = createGame();
    for (let col = 0; col <= 6; col++) {
      expect(isValidDrop(board, col)).toBe(true);
    }
  });

  it('returns false for column -1 (out of range)', () => {
    const { board } = createGame();
    expect(isValidDrop(board, -1)).toBe(false);
  });

  it('returns false for column 7 (out of range)', () => {
    const { board } = createGame();
    expect(isValidDrop(board, 7)).toBe(false);
  });

  it('returns false for a full column (board[0][col] !== 0)', () => {
    const game = createGame();
    game.board[0][3] = 1;
    expect(isValidDrop(game.board, 3)).toBe(false);
  });
});

describe('dropPiece — gravity', () => {
  it('drops into an empty column and lands at row 5 (bottom)', () => {
    const { state: next } = dropPiece(createGame(), 0);
    expect(next.board[5][0]).toBe(1);
  });

  it('drops twice in the same column: second piece lands at row 4', () => {
    let state = createGame();
    ({ state } = dropPiece(state, 0));
    ({ state } = dropPiece(state, 0));
    expect(state.board[5][0]).not.toBe(0);
    expect(state.board[4][0]).toBe(2);
  });

  it('six drops in same column fill rows 5 down to 0', () => {
    let state = createGame();
    for (let i = 0; i < 6; i++) {
      ({ state } = dropPiece(state, 2));
    }
    for (let row = 0; row <= 5; row++) {
      expect(state.board[row][2]).not.toBe(0);
    }
  });
});

describe('turn switching', () => {
  it('after player 1 drops, currentPlayer becomes 2', () => {
    const { state: next } = dropPiece(createGame(), 0);
    expect(next.currentPlayer).toBe(2);
  });

  it('after player 2 drops, currentPlayer becomes 1', () => {
    let state = createGame();
    ({ state } = dropPiece(state, 0));
    ({ state } = dropPiece(state, 1));
    expect(state.currentPlayer).toBe(1);
  });
});

describe('moveCount', () => {
  it('increments moveCount on each valid drop', () => {
    let state = createGame();
    ({ state } = dropPiece(state, 0));
    expect(state.moveCount).toBe(1);
    ({ state } = dropPiece(state, 1));
    expect(state.moveCount).toBe(2);
    ({ state } = dropPiece(state, 2));
    expect(state.moveCount).toBe(3);
  });
});

describe('full column rejection', () => {
  it('7th drop into a full column returns same state unchanged', () => {
    let state = createGame();
    for (let i = 0; i < 6; i++) {
      ({ state } = dropPiece(state, 0));
    }
    const before = state.moveCount;
    const { state: after, row } = dropPiece(state, 0);
    expect(row).toBe(-1);
    expect(after.moveCount).toBe(before);
    expect(after).toEqual(state);
  });
});

describe('checkWin', () => {

  it('returns null on empty board', () => {
    const { state } = dropPiece(createGame(), 0);
    expect(checkWin(state.board, 5, 0)).toBeNull();
  });

  it('detects horizontal win', () => {
    // Place 4 Player 1 pieces in a row: cols 0,1,2,3 at row 5
    let state = createGame();
    for (let col = 0; col < 4; col++) {
      ({ state } = dropPiece(state, col));
      if (col < 3) ({ state } = dropPiece(state, col)); // P2 filler in same col to keep P1 playing
      // Actually: just set board directly for simplicity
    }
    // Direct board setup:
    const board = Array.from({ length: 6 }, () => new Array(7).fill(0));
    board[5][0] = 1; board[5][1] = 1; board[5][2] = 1; board[5][3] = 1;
    const result = checkWin(board, 5, 3);
    expect(result).not.toBeNull();
    expect(result).toHaveLength(4);
  });

  it('detects vertical win', () => {
    const board = Array.from({ length: 6 }, () => new Array(7).fill(0));
    board[5][3] = 1; board[4][3] = 1; board[3][3] = 1; board[2][3] = 1;
    expect(checkWin(board, 2, 3)).not.toBeNull();
  });

  it('detects diagonal-descending win', () => {
    const board = Array.from({ length: 6 }, () => new Array(7).fill(0));
    board[2][0] = 1; board[3][1] = 1; board[4][2] = 1; board[5][3] = 1;
    expect(checkWin(board, 5, 3)).not.toBeNull();
  });

  it('detects diagonal-ascending win', () => {
    const board = Array.from({ length: 6 }, () => new Array(7).fill(0));
    board[5][0] = 1; board[4][1] = 1; board[3][2] = 1; board[2][3] = 1;
    expect(checkWin(board, 2, 3)).not.toBeNull();
  });

  it('returns null for 3-in-a-row (near miss)', () => {
    const board = Array.from({ length: 6 }, () => new Array(7).fill(0));
    board[5][0] = 1; board[5][1] = 1; board[5][2] = 1;
    expect(checkWin(board, 5, 2)).toBeNull();
  });

  it('returns null when pieces are interrupted', () => {
    const board = Array.from({ length: 6 }, () => new Array(7).fill(0));
    board[5][0] = 1; board[5][1] = 2; board[5][2] = 1; board[5][3] = 1;
    expect(checkWin(board, 5, 3)).toBeNull();
  });

});

describe('checkDraw', () => {
  it('returns false when moveCount < 42', () => {
    const state = createGame();
    expect(checkDraw(state)).toBe(false);
  });

  it('returns true when moveCount is 42 and status is playing', () => {
    const state = { ...createGame(), moveCount: 42, status: 'playing' };
    expect(checkDraw(state)).toBe(true);
  });

  it('returns false when moveCount is 42 but status is won', () => {
    const state = { ...createGame(), moveCount: 42, status: 'won' };
    expect(checkDraw(state)).toBe(false);
  });

  it('returns false at moveCount 41', () => {
    const state = { ...createGame(), moveCount: 41 };
    expect(checkDraw(state)).toBe(false);
  });
});

describe('resetGame', () => {
  it('returns a fresh state with empty board', () => {
    const fresh = resetGame();
    fresh.board.forEach(row => row.forEach(cell => expect(cell).toBe(0)));
  });

  it('resets currentPlayer to 1', () => {
    expect(resetGame().currentPlayer).toBe(1);
  });

  it('resets status to playing', () => {
    expect(resetGame().status).toBe('playing');
  });

  it('resets moveCount to 0', () => {
    expect(resetGame().moveCount).toBe(0);
  });

  it('resets winningCells to empty array', () => {
    expect(resetGame().winningCells).toEqual([]);
  });
});
