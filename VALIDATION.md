# Release validation: 2026.11.23.3

The actual-Lua trivia suite passes for shared team bills in 2v2, 3v2 and 4v2 at all four ages, rotating rounding remainders, frozen mixed-age stakes, the unchanged 10% villager fallback, one pass per team per match, answerer-only authority, invalid/late/duplicate requests, answer/pass races, round changes, reassignment, simulated restore, old save compatibility, AI affordability-based pass decisions, teammate suggestions, UI bindings and XAML parsing.

The Content Editor compiled version 2026.11.23.3 with zero errors and warnings. Archive verification confirms all 103 SCAR scripts match release source, all five compiled localization descriptions contain the current version, and no diagnostic markers are included. The installed local archive matches the build. Release SHA-256: `74DFD22C3FD4BA2C463DD277E4964423E08192BC0F530F11D70175C6F83909F0`.

The first upload was rejected for Simplified Chinese localization ID 211, whose inherited value was `3x`. That label now reads `三倍` (three times). A native rebuild and archive inspection verified the corrected compiled text. The in-game checks below used the preceding archive `26D0E18A0076AC238208BABCF62564071B834FD9A4C150C76A129541973EB4B4`; gameplay scripts are byte-identical in the final archive.

Native checks used the clean release archive in an English versus House of Lancaster AI skirmish, without a tuning pack. The pass button rendered above the question, and clicking it before the deadline displayed `Pass used`, `Question passed` and the centre-screen announcement. Resources remained 200 food, 200 wood, 100 gold and 0 stone; both remaining villagers survived. No answer was revealed. The next question retained the disabled `Pass used` control and its timeout applied the normal penalty. Earlier clicks that arrived after the deadline were rejected, left the pass available, and applied the normal timeout penalty. These delayed clicks are not counted as successful pass checks. Team authority and restored state are covered by the automated Lua tests; native multiplayer and save/load remain unverified.

Publication completed on 23 November 2026 as listing **594036**, author **TypeEkcyall**, with description version **2026.11.23.3**. The store download is byte-identical to the final release archive above (318360 bytes; engine version `65c8b8f5e3706ba1bf31b85a418e3287`). The native publisher again created a new listing despite the unchanged project GUID. The rejected upload 594035 never appeared in My Mods. Following the owner's instruction to remove superseded listings, 594034 was deleted; the account's My Mods page now contains only 594036 for Knowledge is Power. The current published copy is enabled in-game, with the local development copy and cached older versions disabled. Existing players should subscribe to https://www.ageofempires.com/mods/details/594036/.

## Previous release validation: 2026.11.23.2

All four automated suites below pass with the teammate advice changes. Additional actual-Lua checks cover sending and changing suggestions, invalid senders and payloads, opposing teams, expired rounds, eliminated players, reassignment, old save data without suggestions, reset between rounds, and UI command routing. Suggestions do not resolve the question, consume RNG, or change resources. Only the assigned answerer can submit the final answer.

The Content Editor compiled this version with zero errors and warnings. Archive verification checks all 103 SCAR scripts against source and all five compiled localization descriptions against VERSION. Diagnostic markers are rejected.

Native checks on 23 November 2026 used the same game build listed below. An isolated diagnostic archive treated the English human and a Delhi AI as trivia teammates and alternated the human between helper and answerer roles. The native menu displayed the question and four options to the helper, automatically opened, sent a clicked suggestion through the native network event, highlighted A, and displayed `TypeEkcyall: A`. A resource snapshot confirmed the suggestion left the question pending and charged nothing. In the answerer role the panel displayed the simulated teammate's name and B suggestion. Subsequent rounds cleared the previous advice. Unanswered questions applied the timeout penalty and displayed the correct answer. Text wrapped without clipping at the tested UI scale.

This role simulation is a single-PC UI check, not a multi-client multiplayer test. Changing advice and final-answer routing pass the automated Lua tests; final-answer clicks during this native advice session missed the deadline, so they are not counted as successful submission checks. The previous release's successful native answer/reward checks are retained below for context.

The diagnostic archive was removed from the active installation after testing. Release SHA-256: `B0004E224384BF05C3BD7747814B36A88256C0EF519B99280722A25FB340A146`.

Publication completed on 23 November 2026 as listing **594034**, author **TypeEkcyall**, description version **2026.11.23.2**. The automatically installed store download matches the clean release archive byte-for-byte. Despite the unchanged project GUID, the native publisher created a replacement listing rather than updating 594033. The old installed version and local development copy are disabled; the latest published copy is enabled. The website rejected an attempt to unlist the old version because its edit form does not offer AoE IV as a game selection. After explicit owner approval, listing **594033** was permanently removed; the account's My Mods page retained only the latest Knowledge is Power listing. Existing subscribers need to subscribe to **594034**.

## Previous release validation: 2026.11.23.1

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

Publication verified in the in-game catalogue on 23 November 2026: listing **594033**, author **TypeEkcyall**, description version **2026.11.23.1**. The automatically installed subscribed archive has the same SHA-256 as the tested build and GitHub release asset. A name search returned one listing.

These are single-PC skirmish checks. Multiple human clients and native save/load are not verified.
