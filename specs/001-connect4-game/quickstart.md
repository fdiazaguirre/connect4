# Quickstart: Connect 4 Game

**Branch**: `001-connect4-game` | **Date**: 2026-04-16

## Prerequisites

- Node.js 18+ (for dev dependencies only — game itself is pure HTML/CSS/JS)
- A modern browser (Chrome, Firefox, Safari, or Edge)

## Setup

```bash
# Clone and enter project
git clone <repo-url> connect4
cd connect4

# Install dev dependencies (testing only)
npm install
```

## Run the Game

Open `src/index.html` directly in a browser, or use any static file server:

```bash
npx serve src
# → opens at http://localhost:3000
```

No build step. No transpilation. Files run as-is.

## Run Tests

### Unit Tests (Vitest)

```bash
# Run all unit tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

### E2e / BDD Tests (Playwright)

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run all e2e tests
npm run test:e2e

# Run with UI mode (interactive)
npx playwright test --ui

# Run a specific test file
npx playwright test tests/e2e/connect4.spec.js
```

## Project Structure

```
src/
├── index.html           # Game page
├── css/styles.css       # Styles + animations
└── js/
    ├── game.js          # Pure game logic (no DOM)
    ├── renderer.js      # DOM rendering + animations
    └── app.js           # Entry point, event wiring

tests/
├── unit/game.test.js    # Vitest unit tests
└── e2e/connect4.spec.js # Playwright BDD tests
```

## Key Commands

| Command | What it does |
|---------|-------------|
| `npm test` | Run unit tests (Vitest) |
| `npm run test:coverage` | Unit tests + coverage report |
| `npm run test:watch` | Unit tests in watch mode |
| `npm run test:e2e` | Run Playwright BDD tests |
| `npx serve src` | Serve game locally |
