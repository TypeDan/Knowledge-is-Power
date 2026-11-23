# Release validation: 2026.11.23.1

## Automated checks

All four scripts pass: `test_trivia.py`, `test_player_settings.py`, `test_population_housing.py`, `test_bonus_hud.py`. They execute the actual Lua with game API stubs. The trivia suite covers 20-second deadlines, 180-second rounds, mixed ages, reordered lobby slots, team pot conservation, affordability, rounded 10% villager casualties, authority checks, duplicate/late submissions, AI odds, shuffled decks, category switches, answerer rotation and UI data binding.

Native AoE player handles cannot be concatenated and separately returned handles are unsuitable as Lua table keys. Player-indexed trivia tables use stable lobby slot numbers. Regression checks cover the displayed personal charge and reward.

## Native game checks

AoE IV 17.0.12303.0, Xbox/Store PC build, 23 November 2026. The Content Editor build completed with zero errors and warnings.

An instrumented local archive used accelerated rounds to inspect all four resource deltas and living villager counts. England and an Order of the Dragon AI formed one team; a Sengoku Daimyo AI formed the other. No tuning pack was selected.

- Correct answer: the two-player team received 150 of each resource per player; the one-player team received 300.
- Wrong answer with sufficient funds: each teammate paid 100 of each resource.
- Insufficient funds: 6 villagers became 5; 8 became 7. Resources were unchanged.
- Clicking the answer button submitted successfully through the native network event and awarded the team.
- Leaving a question unanswered applied the timeout penalty after 20 game seconds.
- Both lobby category controls, readable wrapping, countdown, auto-open and centre-screen announcements rendered.

The instrumented archive is excluded from source and releases. A verifier compares every archived SCAR file against release source and rejects diagnostic markers. The local deployed release archive must match the built archive's SHA-256.

A second skirmish ran the unmodified release archive at normal timing: England versus an Ottoman AI, no tuning pack. The first question opened at three game minutes with 20 seconds available. The menu showed the correct 100-per-resource personal charge. Clicking C (1066, Battle of Hastings) awarded 300 of each resource: food/wood/gold/stone changed from 200/200/100/0 to 500/500/400/300, and the result panel displayed 300 correctly.

Release SHA-256: `5BFAADECF6EFE18A103DB34714F55E5771CEF19FD7C67ED87E6B990E383F8FDC`.

These are single-PC skirmish checks. Multiple human clients and native save/load are not verified.
