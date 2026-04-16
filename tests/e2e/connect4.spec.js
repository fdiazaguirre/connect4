import { test, expect } from '@playwright/test';

test.describe('US1: Drop Piece Into Column', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('first drop lands at bottom row (row 5)', async ({ page }) => {
    // Click a cell in column 3 (any row works for click target)
    await page.click('[data-col="3"]');
    // Piece should appear at row 5, col 3 with class player-1
    const cell = page.locator('[data-row="5"][data-col="3"]');
    await expect(cell).toHaveClass(/player-1/);
  });

  test('status updates to Player 2 after Player 1 drops', async ({ page }) => {
    await page.click('[data-col="3"]');
    await expect(page.locator('#status')).toContainText("Player 2");
  });

  test('second drop in same column lands at row 4', async ({ page }) => {
    await page.click('[data-col="2"]');
    await page.click('[data-col="2"]');
    await expect(page.locator('[data-row="4"][data-col="2"]')).toHaveClass(/player-2/);
  });

  test('full column: 7th drop does not place a piece', async ({ page }) => {
    // Fill column 0 with 6 pieces (alternating players)
    for (let i = 0; i < 6; i++) {
      await page.click('[data-col="0"]');
    }
    // Try 7th drop - status should still show a player's turn (not stuck)
    const statusBefore = await page.locator('#status').textContent();
    await page.click('[data-col="0"]');
    const statusAfter = await page.locator('#status').textContent();
    // moveCount should not have changed (same status)
    expect(statusAfter).toBe(statusBefore);
    // row 0 piece should still be from the 6th drop, not changed
  });

});

test.describe('US2: Win Detection and Announcement', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  // Helper: click a column (clicks the top cell of that column as target)
  // The event delegation in app.js handles any cell click in the column

  test('horizontal win: 4 in a row triggers winner banner', async ({ page }) => {
    // P1: col0, P2: col0 (filler), P1: col1, P2: col1, P1: col2, P2: col2, P1: col3 → win
    const moves = [0, 0, 1, 1, 2, 2, 3];
    for (const col of moves) {
      await page.click(`[data-col="${col}"]`);
    }
    await expect(page.locator('#status')).toContainText('Player 1 wins');
  });

  test('vertical win: 4 stacked in same column triggers winner banner', async ({ page }) => {
    // P1: col0, P2: col1, P1: col0, P2: col1, P1: col0, P2: col1, P1: col0 → P1 vertical win
    const moves = [0, 1, 0, 1, 0, 1, 0];
    for (const col of moves) {
      await page.click(`[data-col="${col}"]`);
    }
    await expect(page.locator('#status')).toContainText('Player 1 wins');
  });

  test('winning cells have winning-cell class', async ({ page }) => {
    const moves = [0, 0, 1, 1, 2, 2, 3];
    for (const col of moves) {
      await page.click(`[data-col="${col}"]`);
    }
    // Wait for win highlight
    await expect(page.locator('.winning-cell').first()).toBeVisible();
    const count = await page.locator('.winning-cell').count();
    expect(count).toBe(4);
  });

  test('post-win: clicking a column does nothing', async ({ page }) => {
    const moves = [0, 0, 1, 1, 2, 2, 3];
    for (const col of moves) {
      await page.click(`[data-col="${col}"]`);
    }
    // Get status text after win
    const statusAfterWin = await page.locator('#status').textContent();
    // Try another click
    await page.click('[data-col="4"]');
    await expect(page.locator('#status')).toHaveText(statusAfterWin);
  });

});

test.describe('US3: Draw Detection', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('full board with no winner triggers draw message', async ({ page }) => {
    // Fill board in a pattern that avoids 4-in-a-row
    // Alternating columns to prevent vertical/horizontal wins
    const pattern = [0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6];
    for (const col of pattern) {
      await page.click(`[data-col="${col}"]`);
    }
    await expect(page.locator('#status')).toContainText("draw");
  });

  test('post-draw: clicking a column does nothing', async ({ page }) => {
    const pattern = [0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6];
    for (const col of pattern) {
      await page.click(`[data-col="${col}"]`);
    }
    const statusAfterDraw = await page.locator('#status').textContent();
    await page.click('[data-col="0"]');
    await expect(page.locator('#status')).toHaveText(statusAfterDraw);
  });

});

test.describe('US4: New Game Reset', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('reset button clears board and resets to Player 1', async ({ page }) => {
    // Play a few moves
    await page.click('[data-col="0"]');
    await page.click('[data-col="1"]');
    // Reset
    await page.click('#reset-btn');
    // Board should be empty
    const pieces = await page.locator('.cell.player-1, .cell.player-2').count();
    expect(pieces).toBe(0);
    // Status should show Player 1
    await expect(page.locator('#status')).toContainText('Player 1');
  });

  test('reset after win clears highlights and board', async ({ page }) => {
    const moves = [0, 0, 1, 1, 2, 2, 3];
    for (const col of moves) {
      await page.click(`[data-col="${col}"]`);
    }
    // Win triggered
    await expect(page.locator('.winning-cell').first()).toBeVisible();
    // Reset
    await page.click('#reset-btn');
    // Highlights gone
    const highlights = await page.locator('.winning-cell').count();
    expect(highlights).toBe(0);
    // Board empty
    const pieces = await page.locator('.cell.player-1, .cell.player-2').count();
    expect(pieces).toBe(0);
  });

});
