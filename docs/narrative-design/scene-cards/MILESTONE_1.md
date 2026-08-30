# Scene cards — Milestone 1

Eight new storylets, written before the prose and re-checked against it after.

Two things these cards are enforcing, both learned the expensive way:

**Every state change is declared.** If a choice moves a relationship or grants a
fact, it appears in the storylet's `effects` or `outcomes`. A change that exists
only in prose is invisible to the reachability analysis, which then reports the
content depending on it as dead.

**Nothing here decides what September 32 is.** Scenes may produce evidence,
rumour, interpretation and confident error. They may not produce answers.

---

## Architectural requirements this set exercises

| Requirement | Where |
| --- | --- |
| 3 delayed callbacks | `dorm_message`, `mara_older_story`, `noah_evening_layout` |
| 2 commitments | `june_the_favour`, `noah_asks_for_access` |
| 4 knowledge transitions | `june_welcome_pack`, `mara_older_story` ×2, `noah_asks_for_access` |
| 3 non-trust relationship axes | respect, resentment, suspicion, dependency, attraction, familiarity throughout |
| 2 NPC↔NPC effects | `mara_reads_the_room`, `noah_asks_for_access` |
| 2 trait-gated choices | `dorm_message`, `mara_reads_the_room` |
| 1 contradictable belief | `mara_older_story` → `suspects(photo_is_a_forgery)` |

---

## 1. `june_the_favour`

```
STATUS          prototype
CHARACTERS      June
LOCATION        courtyard
TIME            midday, afternoon
PHASE           any

PURPOSE
    Establish June as a person with a Tuesday. She wants something today and it
    has nothing to do with the archive.

NARRATIVE FUNCTION
    Introduces June. Creates the first commitment that is not about the mystery,
    so that breaking one can cost something social rather than evidential.

EMOTIONAL START   Neutral; you are crossing a courtyard.
EMOTIONAL END     Mildly obligated, in a way that is pleasant.

CHARACTERS KNOW
    June: that she is good at organising things and tired of being asked.
    Player: nothing about her.

CHARACTERS DON'T KNOW
    Player does not know she is avoiding someone. It is not stated.

PLAYER MAY LEARN
    Nothing factual. This scene grants no knowledge, deliberately.

PLAYER MUST NOT LEARN YET
    Why she transferred. Not raised.

SETUPS      The favour, which comes due in dorm_message.
PAYOFFS     None. This is a first appearance.

CHOICES
    Agree easily        — gentle. familiarity, and she is briefly embarrassed.
    Ask what it is first— skeptical. respect up, familiarity flat.
    Say no, warmly      — direct. respect up, no commitment created.

STATE EFFECTS
    commit(june_favour, june, 1, 45) on the two accepting branches
    See `outcomes` in data/storylets/june_the_favour.json

CONTINUITY RISKS
    Must not reference the archive. June has not been in it.
```

---

## 2. `june_welcome_pack`

```
STATUS          prototype
CHARACTERS      June
LOCATION        classroom_2b
TIME            any
PHASE           any

PURPOSE
    June's kind of local knowledge — an outsider's, from a document she skimmed
    once — as distinct from Mara's, which is oral and inherited.

NARRATIVE FUNCTION
    First inconsistency that is not in the archive. It arrives from someone who
    finds it boring, which is the correct temperature for the normal phase.

EMOTIONAL START   Companionable, slightly bored.
EMOTIONAL END     Ordinary. Nothing has been solved and nothing feels wrong.

CHARACTERS KNOW
    June: the printed school history has a gap. She thinks it is a misprint and
        has thought about it for a total of ninety seconds, two years ago.
    Player: possibly that box 17 has an unlisted photograph.

CHARACTERS DON'T KNOW
    Neither knows the gap and the photograph are related. They may not be.

PLAYER MAY LEARN
    school_history_skips_a_year   (known)

PLAYER MUST NOT LEARN YET
    Which year. June does not remember and does not care enough to check.
    Withholding the number is the whole discipline of this scene.

SETUPS      The gap. Mara's older story is about the same absence from the
            other direction, and neither scene says so.
PAYOFFS     None yet.

CHOICES
    Which year was it?   — curious. She does not know. familiarity.
    A misprint, then.    — skeptical. She is relieved. Her stance hardens.
    Change the subject.  — gentle. familiarity, attraction. Nothing learned.

STATE EFFECTS
    know(school_history_skips_a_year, junes_welcome_pack) on two branches
    npc_stance(june, school_history_skips_a_year, known)

CONTINUITY RISKS
    June must not sound like she is presenting a clue. She is complaining about
    a booklet.
```

---

## 3. `mara_reads_the_room`

```
STATUS          prototype
CHARACTERS      Mara
LOCATION        hallway_east
TIME            morning, midday
PHASE           any

PURPOSE
    Mara's competence, and its cost. She reads the social weather accurately and
    trusts the reading, and one of the things she says is wrong.

NARRATIVE FUNCTION
    Establishes her as a source who is usually right — which is what makes her
    being wrong later worth anything.

EMOTIONAL START   Passing conversation.
EMOTIONAL END     You know something about the school you did not, and one
                  thing you have no way to check.

CHARACTERS KNOW
    Mara: who is talking to whom. Correct about Theo and Iris. Confidently
        wrong about why June sits alone at lunch.
    Player: whatever they have accumulated.

CHARACTERS DON'T KNOW
    Mara does not know she is wrong about June, and will not check.

PLAYER MAY LEARN
    Nothing factual — this is characterisation and NPC state.

PLAYER MUST NOT LEARN YET
    That she is wrong. The scene must not signal it. A player who has met June
    may notice; a player who has not should hear a reliable person being
    reliable.

SETUPS      Mara's false confidence about June.
PAYOFFS     june_the_favour, if the player has seen it — they now hold a
            contradiction the game has not pointed at.

CHOICES
    Agree with her       — familiarity. She warms.
    [Perceptive] Push back about June — empathetic ≥ 2. respect up, and she
                           goes quiet. mara->june suspicion rises anyway.
    Ask about Theo       — curious. Accurate information, freely given.

STATE EFFECTS
    NPC↔NPC: rel mara->june.suspicion += 2 on two branches
    npc_stance(mara, theo_checks_the_ledger, known)

CONTINUITY RISKS
    theo_checks_the_ledger stays NPC-side. The player does not acquire it here.
```

---

## 4. `mara_older_story`

```
STATUS          prototype
CHARACTERS      Mara
LOCATION        town_road
TIME            afternoon, evening
PHASE           any

PURPOSE
    The town's account of itself, offered by someone who knows it is an account.
    And the first interpretation of the photograph that is not the player's.

NARRATIVE FUNCTION
    Delayed callback: only available once the player knows the photograph
    exists. Introduces a belief the story may later contradict.

EMOTIONAL START   A walk. Genuinely pleasant.
EMOTIONAL END     She has given you something and is not sure she should have.

CHARACTERS KNOW
    Mara: a family version of why one year has no yearbook. She knows it is a
        version and will say so.
    Player: old_photo_exists.

CHARACTERS DON'T KNOW
    Mara has never been in the archive and does not know what is in box 17.

PLAYER MAY LEARN
    mara_knows_the_older_story  (known — that she HAS an account, not what it is)
    photo_is_a_forgery          (SUSPECTED — her interpretation, offered as one)

PLAYER MUST NOT LEARN YET
    The contents of the account. Still IDEA in canon. She declines, in
    character, and the decline is the scene.

SETUPS      photo_is_a_forgery as a live, plausible, unverified reading.
PAYOFFS     old_photo_glimpse.

CHOICES
    Ask her to tell it     — curious. She does not. trust and resentment both
                             move; asking cost something.
    Let it go              — gentle. trust, respect. She offers the forgery
                             reading unprompted, because you did not push.
    Say the town is strange— direct. suspicion +4. The one wrong answer, and
                             it is wrong socially, not morally.

STATE EFFECTS
    know(mara_knows_the_older_story, mara_on_the_road)
    suspect(photo_is_a_forgery, mara_thinks_someone_faked_it)
    npc_stance(mara, old_photo_exists, suspected)

CONTINUITY RISKS
    photo_is_a_forgery contradicts photo_dated_sept_32. The player may end up
    holding both. That is intended and the engine tracks it (rule R8).
    It must NOT be granted as `known`.
```

---

## 5. `noah_asks_for_access`

```
STATUS          prototype
CHARACTERS      Noah
LOCATION        courtyard
TIME            midday, afternoon
PHASE           any

PURPOSE
    Introduce Noah, and the pressure to publish. He tells you exactly what he
    wants, which is what makes him difficult.

NARRATIVE FUNCTION
    Second commitment. First NPC↔NPC consequence with a cost the player can
    see coming and take anyway.

EMOTIONAL START   Ambushed, pleasantly.
EMOTIONAL END     You have either promised him something or refused him, and
                  neither is comfortable.

CHARACTERS KNOW
    Noah: that something is going on in the archive, in outline. That Iris has
        said "not yet" four times.
    Player: whatever they hold.

CHARACTERS DON'T KNOW
    Noah does not know any specifics. He is not being coy; he has none.

PLAYER MAY LEARN
    noah_is_writing_about_the_archive  (known)

PLAYER MUST NOT LEARN YET
    Nothing about the phenomenon. Noah has no information to give.

SETUPS      The promise, and Iris's reaction to being volunteered.
PAYOFFS     None.

CHOICES
    I'll ask her          — commitment created. familiarity.
    Ask her yourself      — direct. respect up, resentment up.
    Tell him what's in the box — curious. NPC↔NPC: iris->noah suspicion +3,
                            and iris->player trust DOWN. The interesting one.

STATE EFFECTS
    know(noah_is_writing_about_the_archive, he_told_me)
    commit(noah_access, noah, 2, 55) on branch one
    rel iris->noah.suspicion += 3 and rel iris.trust -= 2 on branch three

CONTINUITY RISKS
    Branch three requires the player to know something. If they do not, it must
    read as them repeating a rumour — which is worse, and fine.
```

---

## 6. `noah_evening_layout`

```
STATUS          prototype
CHARACTERS      Noah
LOCATION        classroom_2b
TIME            evening, night
PHASE           any

PURPOSE
    Noah unbothered by something odd, with an ordinary reason available. The
    three readings must all survive this scene.

NARRATIVE FUNCTION
    Delayed callback on knowing what he is writing. Tests whether the prose can
    hold ambiguity without signalling.

EMOTIONAL START   Late, tired, companionable.
EMOTIONAL END     Unresolved, and not ominously so.

CHARACTERS KNOW
    Noah: the paper's back issues are incomplete. He finds this administratively
        annoying and not interesting.
    Player: noah_is_writing_about_the_archive.

CHARACTERS DON'T KNOW
    Whether the gap in the back issues is the same gap as anything else.
    Neither raises it.

PLAYER MAY LEARN
    Nothing factual. Deliberately.

PLAYER MUST NOT LEARN YET
    Whether Noah has noticed. The scene must not answer it.

SETUPS      A third absence, unremarked.
PAYOFFS     noah_asks_for_access.

CHOICES
    Doesn't that bother you? — He gives an ordinary reason. It is a good one.
    Help with the layout     — gentle. familiarity, dependency +2.
    [Observant] The gap is the same length — curious ≥ 3. He agrees it is a
                            coincidence. He may be right.

STATE EFFECTS
    rel noah.familiarity, rel noah.dependency on branch two

CONTINUITY RISKS
    No line may imply Noah is concealing anything. Check every beat against
    docs/characters/noah.md, "The three readings".
```

---

## 7. `dorm_message`

```
STATUS          prototype
CHARACTERS      none (alone)
LOCATION        dorm_room
TIME            evening, night
PHASE           any

PURPOSE
    Make the dorm mechanically and emotionally useful: the room where the day
    is settled and a promise is kept or is not.

NARRATIVE FUNCTION
    The main delayed callback. Reads commitment state and relationship state
    and produces a different scene from the same file.

EMOTIONAL START   Tired.
EMOTIONAL END     Depends entirely on what the player has already done.

CHARACTERS KNOW
    Player: whatever they hold.

PLAYER MAY LEARN
    Nothing new. This scene consolidates.

PLAYER MUST NOT LEARN YET
    n/a

SETUPS      None.
PAYOFFS     june_the_favour, noah_asks_for_access, meet_theo_archive, and the
            photograph if they are carrying it.

CHOICES
    Answer June       — fulfils june_favour if open.
    Leave it till morning — breaks it. Real cost, taken knowingly.
    [Observant] Look at the photograph again — curious ≥ 3. Requires the item.

STATE EFFECTS
    Branch-dependent; declared in outcomes.

CONTINUITY RISKS
    The scene must not assume any particular earlier scene was played. Every
    reference is guarded.
```

---

## 8. `town_road_evening_walk`

```
STATUS          prototype
CHARACTERS      none
LOCATION        town_road
TIME            evening
PHASE           any

PURPOSE
    Make the world larger than the school, and make the road ordinary. Its
    ordinariness is an asset the story will spend later.

NARRATIVE FUNCTION
    Repeatable ambient content that is NOT the courtyard — the direct answer to
    a single ambient storylet accounting for 72% of played scenes.

EMOTIONAL START   Wherever the player was.
EMOTIONAL END     Slightly calmer.

CHARACTERS KNOW    n/a
PLAYER MAY LEARN   Nothing.

PLAYER MUST NOT LEARN YET
    The road is not haunted. It must not be foreshadowed as haunted. Three
    variants, all mundane, none ending on an ominous line.

SETUPS      A normal road, established at length, cheaply.
PAYOFFS     None.

CHOICES     None. Some scenes are texture.

STATE EFFECTS
    event(walked_into_town)

CONTINUITY RISKS
    Must work at any point in the run and after any combination of scenes.
```
