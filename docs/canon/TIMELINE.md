# Timeline

**Status: PROVISIONAL**

Two timelines, kept apart on purpose. Confusing them is how a project ends up
with a scene that contradicts a document it has already shown the player.

## In-fiction, present day

The run starts on **September 1** and is measured in `day` (run day, from 1) and
`calendar_day` (in-fiction date). They are separate numbers because the
in-fiction calendar is the thing that misbehaves.

| Run day | Beat | Status |
| --- | --- | --- |
| 1, morning | Arrival. Met at the gate. Assigned to the archive. | `anchor: arrival` |
| 1, midday | First shift. The job, the room, the people. | `anchor: first_shift` |
| 1–2 | Ordinary days. Box seventeen. The photograph surfaces. | storylets |
| 2+ | **The date.** The stamp, read twice. Phase advances to `odd`. | `anchor: the_date` |
| — | Everything after this is unwritten. | `IDEA` |

The prototype stops before the third anchor. That is deliberate: the slice exists
to prove the systems work, and revealing September 32 in a systems demo would
spend the reveal for nothing.

## In-fiction, historical

**Undecided.** `IDEA`

What is fixed is only the shape:

- The archive covers several decades. Its exact span is undecided.
- There is at least one year for which the school did not print a yearbook. Mara
  has heard a family account of why. `PROVISIONAL`
- Box seventeen's contents predate everyone currently at the school.
- The accession ledger runs to at least three volumes, ninety-one pages, and
  every column on every page carries a date. Except one. `PROVISIONAL`

**Nothing here should be pinned down further until the phenomenon's constraints
are settled.** A historical date invented for one scene becomes a fact the ending
has to accommodate, and the cost of that is invisible until it is large.

## Out of fiction

| Date | Event |
| --- | --- |
| 2026-08-30 | Project bootstrapped. Ren'Py 8.5.3, storylet engine, asset pipeline, vertical slice. |

## Rules for editing this file

1. A date added here is a commitment. Add it only when a scene actually needs it.
2. When a date changes, grep the `.rpy` sources for it before saving.
3. Historical dates are `IDEA` until an anchor scene depends on one.
