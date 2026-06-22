# DECISIONS — the "why"
> Repo: https://github.com/sadeqnotion1/OfflineFeed
>
> **Append-only.** Never rewrite history; add a new entry. Each decision gets an
> id (D1, D2, ...), a date, the decision, and the reason. Record a decision the
> moment it's made so we don't re-litigate it later.

---

## D1 — 2026-06-22 — Adopt the `.agents/` brain for OfflineFeed
**Decision:** Use this `.agents/` brain as the single source of truth for AI sessions on OfflineFeed.
**Why:** Zero-context-loss handoffs between chats/models; no re-explaining state.

## D2 — 2026-06-22 — Capture the 23-item list as a 10-milestone roadmap
**Decision:** Turn the maintainer's bug/feature list into ordered milestones M1–M10 (see ROADMAP.md),
ordered visual-foundation → settings → icons → image correctness → channel info → telegram → copy
→ reader → backend → loading.
**Why:** Each milestone is ~one chat, groups items that touch the same files, and front-loads the
visual foundation (window/theme/icons) that later UI work depends on. Ordering is the maintainer's
to change anytime in ROADMAP.md.

## D3 — 2026-06-22 — Do not replace OfflineFeed's working run files
**Decision:** The brain is additive only. OfflineFeed already has working `run.bat` / `run.sh`
(→ `python backend/run_offlinefeed.py`); the starter pack does NOT overwrite them.
**Why:** Delivery Standard §1 — never break what already works.
