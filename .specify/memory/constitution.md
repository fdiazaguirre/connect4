<!--
SYNC IMPACT REPORT
Version change: (template) → 1.0.0
Modified principles: N/A (initial ratification)
Added sections: Core Principles (I–IV), Technology Context, Governance
Removed sections: N/A
Templates requiring updates:
  ✅ plan-template.md — Constitution Check section already generic; no update required
  ✅ spec-template.md — no principle-specific references; no update required
  ✅ tasks-template.md — no principle-specific references; no update required
Follow-up TODOs: none
-->

# Connect 4 Constitution

## Core Principles

### I. Correctness First

Game logic MUST be bug-free and fully rule-compliant at all times.

- Board state transitions MUST enforce all Connect 4 rules (valid column drops, full-column detection, win detection in all 4 directions, draw detection)
- Win and draw detection MUST be deterministic and fully covered by tests
- No move MUST alter board state if it violates rules
- Any rendering or visual layer MUST NOT bypass or mask incorrect game state

### II. Responsive UI

User interactions MUST produce visible feedback within 100ms. Animations MUST NOT block gameplay.

- Disc drop and win animations MUST be non-blocking (async, CSS/RAF-based)
- UI MUST remain interactive during animation playback
- Initial page load MUST NOT require heavy runtime downloads; keep bundle lean
- Target: 60 fps during all animated transitions

### III. Playability

Game MUST be immediately playable without instructions. UX decisions MUST reduce friction.

- Current player MUST always be clearly indicated
- Valid drop columns MUST be visually distinguishable on hover
- Win result MUST be unambiguous (highlight winning discs + message)
- Game reset MUST be one action from any state (win, draw, mid-game)

### IV. Visual Engagement

Visual effects MUST enhance immersion without compromising Correctness or Responsiveness.

- Effects MUST be additive (removal degrades delight, not correctness)
- No effect MUST delay the next player's input by more than one animation cycle
- Effects MUST respect `prefers-reduced-motion` accessibility media query
- Particle, glow, or highlight effects on win/drop are encouraged; MUST not obscure board state

## Technology Context

Platform: browser-based web game (HTML/CSS/JS or framework of choice).
No server required for single-player / local-multiplayer mode.
Tech stack decisions deferred to specification phase; MUST align with Responsiveness principle (no heavy runtimes).

## Governance

- Constitution supersedes all other practices; PRs MUST verify compliance with all four principles
- Amendments follow semantic versioning: MAJOR for principle removal/redefinition, MINOR for new principle/section, PATCH for wording/clarification
- All complexity MUST be justified against these principles; YAGNI applies beyond them
- Amendments require rationale, approval, and update to `LAST_AMENDED_DATE`

**Version**: 1.0.0 | **Ratified**: 2026-04-16 | **Last Amended**: 2026-04-16
