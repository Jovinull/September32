# Art gap analysis

What exists, what is missing, and what closing each gap would take.

Classification:

| | |
| --- | --- |
| **FREE ASSET SUFFICIENT** | Installed and adequate for the finished game. |
| **NEEDS EDIT** | Exists; needs deterministic processing or reframing. |
| **CAN BUILD IN-HOUSE** | Producible with code or non-artistic tooling. |
| **NEEDS COMMISSION** | Requires an artist. |

---

## Characters

| Need | Status | Notes |
| --- | --- | --- |
| Five students, school uniforms | **FREE ASSET SUFFICIENT** | A01: 5 characters × 2 uniforms × 17 expressions. |
| Casual outfits for iris, theo | **FREE ASSET SUFFICIENT** | A02, three outfits each. |
| Casual outfits for mara, june, noah | **NEEDS COMMISSION** | A02's free tier does not include these three. Three characters who are *from* the town or defined outside school, with no clothes but a uniform. |
| Ms. Ellery (faculty) | **NEEDS COMMISSION** | The Sensei pack scored 3.4/10 and was rejected. She currently speaks with no sprite. |
| Any male-presenting sprite | **NEEDS COMMISSION** | Kioshi & Haruo scored 3.4/10. The cast is currently all one presentation, which is a casting constraint imposed by asset availability and should not be mistaken for a design decision. Open in `docs/canon/OPEN_QUESTIONS.md`. |
| Iris holding a camera | **NEEDS COMMISSION** | Her defining object, and she cannot be shown with it. |
| Theo holding the ledger | **NEEDS COMMISSION** | Same problem. |

---

## Backgrounds

| Need | Status | Notes |
| --- | --- | --- |
| Classrooms, hallways, club room, entrance, roof, stairs | **FREE ASSET SUFFICIENT** | 114 images with day/evening/night variants. |
| Art room, music room, pool | **FREE ASSET SUFFICIENT** | 90 images. |
| Bedrooms and dorms | **FREE ASSET SUFFICIENT** | 37 images, three rooms. |
| General exteriors: beach, café, city, park, house | **FREE ASSET SUFFICIENT** | 41 images from the starter pack. |
| **The archive room** | **NEEDS COMMISSION** | Currently played by a club-room background. The most-seen location in the game, and the one place that should look like itself: boxes to the ceiling, a scanner that predates everyone, a kettle. |
| The town | **NEEDS EDIT** or commission | Currently a house exterior. Mara's whole character is about this place and it has no face. |
| Night-time archive | **NEEDS EDIT** | Variants exist; needs the grading pipeline pointed at them. |

---

## Documents and photographs

This is the category that matters most, and the one with the least support.

| Need | Status | Notes |
| --- | --- | --- |
| Paper, card and stamp textures | **CAN BUILD IN-HOUSE** | Deterministic, procedural, no model. `s32_engine`-adjacent tooling; the archival treatment in `process.py` is the same technique. |
| A ledger page with a column and no header | **CAN BUILD IN-HOUSE** | Rules, columns, a hand-like font, the missing header. Entirely constructible. |
| Catalogue cards, filing marks, accession numbers | **CAN BUILD IN-HOUSE** | Text plus texture. |
| Newspaper and student-paper layouts | **CAN BUILD IN-HOUSE** | Typesetting. |
| **The class photograph** | **NEEDS COMMISSION** | Forty faces in three rows, everybody squinting, a brown stamp in the corner. The single most important image in the game. **It must not be AI-generated** — see `docs/legal/AI_AND_ASSETS_POLICY.md`, which rules out generating fake photographs of people categorically, and not only for legal reasons. |
| Other in-fiction photographs | **NEEDS COMMISSION** | Same constraint. |

---

## UI

| Need | Status | Notes |
| --- | --- | --- |
| Buttons, sliders, checkboxes | **FREE ASSET SUFFICIENT** | Kenney, CC0, 82 neutral greys — scaffolding only. |
| Inventory and clue icons | **NEEDS EDIT** | 163 Kenney items with archival treatment applied. Adequate; not distinctive. |
| The project's own interface | **NEEDS COMMISSION** | The shipped game must not read as "Kenney UI". `docs/style/VISUAL_DESIGN_SYSTEM.md` has the direction. |
| The archive viewer | **NEEDS COMMISSION** | The second most important interface in the game and currently unbuilt. |
| The calendar | **CAN BUILD IN-HOUSE** | And it is the best idea the project has: a calendar that quietly accepts `30 31 32`. |

---

## Audio

| Need | Status | Notes |
| --- | --- | --- |
| Menu, cheerful, emotional, dramatic, unease | **FREE ASSET SUFFICIENT** | Five tracks, BGM Pack 1. |
| School daytime ambience | **NEEDS COMMISSION** or CC0 search | The `normal` phase has one cheerful track and needs three or four. |
| Investigation and archive | **NEEDS COMMISSION** | Nothing appropriate. |
| Romance | **NEEDS COMMISSION** | Nothing appropriate. |
| Revelation, the `impossible` phase | **NEEDS COMMISSION** | Nothing appropriate. |
| Sound effects | **NEEDS COMMISSION** or CC0 search | None installed. Paper, a scanner, rain, a door. |

---

## Key art

| Need | Status |
| --- | --- |
| Title screen | **NEEDS COMMISSION** |
| Steam capsule art | **NEEDS COMMISSION** |
| Event CGs | **NEEDS COMMISSION** |

---

## Priority, if a budget existed

1. **The class photograph.** The game's central object.
2. **The archive room background.** The most-seen location.
3. **Casual outfits for mara, june, noah.** Three characters currently unable to
   be off-duty.
4. **Ms. Ellery.** A named character with no face.
5. **A male-presenting sprite.** Removes a constraint the design did not choose.
6. **The archive document viewer.** More important than any CG.
7. **Music for the later phases.**

## Priority with no budget

1. Document generation tooling — procedural paper, cards, ledgers, the calendar.
   Real progress on the game's most distinctive interface, using code.
2. Point the grading pipeline at the night and evening background variants.
3. CC0 audio search, under the same licence discipline.
