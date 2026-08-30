# World

**Status: PROVISIONAL** — every proper noun here is a placeholder and marked as
such. See `OPEN_QUESTIONS.md`.

## The school — `PROVISIONAL`

A small residential academy. The gate says **Northfield** in iron, with the F
missing; nobody has fixed it and at this point nobody would. A few hundred
students. Old enough to have an archive worth digitising, small enough that
everyone knows who is doing the digitising.

Physically it is what the installed backgrounds support: classrooms, hallways
with numbered doors, a club room now serving as the archive, an entrance, a
rooftop with a door that does not lock, stairs, a courtyard, an art room, a music
room, a pool. Residential blocks with small rooms that came furnished.

The rooftop matters. Half the school knows the door does not lock and nobody says
so out loud, which is a good working description of the school in general.

## The archive — `PROVISIONAL`

A club room until recently. There is still a kettle. Boxes to the ceiling on two
walls; a flatbed scanner on the third that predates everyone in the room.

The digitisation project is real institutional work with a real deadline that
nobody enforces. The list of what is in the boxes is a photocopy of a typed list,
corrected in pencil, twice, in two different hands. Box seventeen has been box
seventeen for three weeks.

**Ms. Ellery** supervises. She decides what gets catalogued and what gets a box
at the back. She is not sinister; she is the institution, which is different and
worse.

## The town — `PROVISIONAL`

Small. The school is the largest employer and the largest archive. Families like
Mara's have been here long enough that the town's account of itself is also a
family account, and the two are hard to separate — which is Mara's entire
situation.

Undecided: the country, the region, the era. See `OPEN_QUESTIONS.md`. The writing
is deliberately non-specific about all three, and so far this has cost nothing.

## Time — `PROVISIONAL`

The game runs on days divided into seven slots (`early_morning` through
`late_night`). The in-fiction calendar starts on **September 1** and advances one
day at a time, which is why `calendar_day` is a separate number from `day` and
why the month is a string rather than a computed date. The whole point of the
story is that this calendar does not behave, and a `datetime` would refuse to
represent that.

Weather is a daily Markov chain (`s32_engine.world.TRANSITIONS`) — persistent
enough to plan around, varied enough that a scene gated on rain is something a
patient player can wait for rather than a lottery.
