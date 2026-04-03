# Why Startups Need a Free Self-Hosted Security Baseline

Published: 2026-04-02

Early-stage teams need security feedback but often cannot justify expensive enterprise platforms. A free self-hosted baseline allows teams to start now and scale controls later.

## Common startup constraints
- Limited security budget
- Small engineering team
- Need to keep source code private
- Fast release cadence

## What works in practice
Use a layered model:
1. Baseline automated scans in CI (`quick` profile).
2. Deeper scans for release candidates (`deep` profile when enabled).
3. One place to review findings and prioritize fixes.

## eidosSec documentation model
To avoid confusion, docs separate:
- Current baseline capabilities (`docs/tools.md`)
- All-in-one expansion roadmap (`docs/INTEGRATED_APP_PLAN.md`)
- API/runtime contract (`docs/api.md`, `docs/installation.md`)

## Bottom line
The best first step is a repeatable local baseline that developers can run every day. Coverage can expand over time, but consistency should start immediately.
