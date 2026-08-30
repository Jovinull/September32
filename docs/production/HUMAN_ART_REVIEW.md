# Human art review

Some questions about artwork can only be answered by a person looking at it.
This is the list of them.

## Why this file exists

[ADR-0003](../decisions/ADR-0003-asset-licensing.md) forbids sending third-party
artwork to any AI or vision service — not for analysis, not for tagging, not for
"just looking at it". The licences under which the packs were obtained do not
grant that, and a redistribution question is not the kind of thing to be casual
about.

The consequence is that Claude, and any other assistant working in this
repository, **cannot open a vendor image**. It can measure one: the audit tooling
is local, deterministic and reads pixels with Pillow, which is why questions like
[`purp`](ASSET_NAMING.md) could be settled at all. But measurement is not
seeing, and some things need seeing.

So this file is the boundary. Everything on it is a small job for a human with
the contact sheets open, and nothing on it blocks the current milestone.

## How to look

Generate the contact sheets, which are local and disposable:

```bash
uv run s32 assets sheets
```

They land in `tools/reports/contact-sheets/`. That directory is git-ignored —
these are derived from third-party art and must not be committed
([ADR-0003](../decisions/ADR-0003-asset-licensing.md)).

Do not upload them anywhere. Do not paste them into a chat with an assistant.
Open them in an image viewer.

## Open items

### 1. Confirm `purp` really means gloom

**Status:** measured, not seen. Mapped to `gloom` in
`tools/s32tools/assets/naming.py`.

Local measurement says `purp` edits the same facial region as the other
expressions, but in violet (268–279°) rather than skin tones (7–31°), and
reaches higher up the forehead. That reads as the anime convention for
gloom or dread. The full evidence is in [`ASSET_NAMING.md`](ASSET_NAMING.md).

**What to check:** open one `*_purp.webp` beside the same character's
`*_neutral.webp` and `*_sad.webp`.

- Is it a mood — shadow over the face, dread or gloom — rather than a costume
  colour? If not, the mapping is wrong and should come straight back out.
- Is `gloom` the right word, or is it closer to `dread`, `shocked` or
  `despair`? The name is ours to choose; pick the one a writer would reach for.
- Is it distinguishable from `sad` at a glance? If it is not, scenes should
  never depend on the difference, and the fallback chain
  `gloom → sad → concerned → neutral` is doing its job.

Until this is ticked, no scene should turn on the gloom/sad distinction.

### 2. Confirm the expression mappings that were inferred from the filename

**Status:** unverified, low risk.

Most of `EXPRESSIONS` in `naming.py` is a direct rename (`happy` → `happy`).
Six are interpretations of the pack's vocabulary:

| source | ours | worth a glance because |
| --- | --- | --- |
| `upset` | `sad` | could be closer to `angry` |
| `upsettalk` | `sad_talk` | same |
| `tears` | `crying` | probably right; cheap to confirm |
| `huh` | `surprised` | could be confusion rather than surprise |
| `frown` | `concerned` | could be disapproval rather than worry |
| `evilsmirk` | `smirk` | ours drops the "evil"; check it is not too smug for an ordinary scene |

### 3. Confirm the character casting still holds

**Status:** unverified.

`data/characters/*.json` assigns a vendor character to June, Mara, Noah, Iris
and Theo. Milestone 1 gave all three of the new characters written voices for
the first time — see [`../characters/VOICES.md`](../characters/VOICES.md).

**What to check:** read each character's "Writing constraints" section, then
look at the sprite. Mara in particular is written flat, still and watchful; if
the assigned sprite is bubbly at rest, the casting is fighting the prose and one
of the two should change. Say which.

### 4. The class photograph

**Status:** NEEDS COMMISSION. Not a review item — a gap.

There is no art for the photograph the plot turns on. It renders as a marked
placeholder inside the document viewer and is asserted to stay that way by
`tests/test_documents.py::test_the_class_photograph_is_still_a_declared_gap`.

It must not be resolved by generating an image, by downloading an unrelated
school photograph, or by quietly using a picture of real people. See
[`ART_GAP_ANALYSIS.md`](ART_GAP_ANALYSIS.md).

## What must never appear on this list

A task phrased as "have the assistant look at the artwork and tell us what it
is". If a question needs eyes, it needs human eyes, and it belongs here rather
than in a prompt.
