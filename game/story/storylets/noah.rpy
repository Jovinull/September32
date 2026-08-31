# PROTOTYPE / NON-FINAL
#
# Noah. Scene cards: docs/narrative-design/scene-cards/MILESTONE_1.md
# Voice: docs/characters/VOICES.md and docs/characters/noah.md
#
# HARD CONSTRAINT, checked line by line: all three readings of Noah must survive
# these scenes — he knows something / he does not care / you are reading too much
# into him. Wherever he is unbothered, an ordinary reason is on the page, and the
# prose does not choose between them.
#
# Effects are declared in data/storylets/noah_*.json.

label s32_st_noah_asks_for_access:

    scene bg courtyard day with dissolve
    show noah school_summer neutral at s32_right with dissolve

    c_noah "Right, you're the archive one, I've been meaning to catch you, I'm not being weird about it I just genuinely have not been in the same room as you until now."

    narrator "He has said all of that in one breath and is already reaching into his bag."

    c_noah "Noah. I do the paper."

    c_me "I've seen the paper."

    c_noah "You've seen four pages and a printing error, but thank you."

    show noah school_summer happy

    c_noah "I want twenty minutes in that room with a camera. That's the whole ask."

    narrator "He does not lower his voice. Two people walk past. He waits for them and then continues at the same volume."

    c_noah "I'm not being coy, so I'll just tell you the rest of it: I'd run it as a piece about the digitisation. Two hundred words, a photo of the boxes, someone saying it's important work."

    c_noah "I've asked Iris four times. She says not yet. She says it the same way each time, which I've decided is a good sign."

    menu:
        "I'll ask her for you.":
            $ rel("noah->player", "familiarity", 3)
            $ promise("noah_access", "noah", in_days=2, importance=55)

            c_noah "Would you? That's — yes. Thursday's fine. Any day's fine."

            c_noah "Tell her I'll leave the camera outside if that's the thing. It usually is the thing."

            narrator "He writes something in the corner of a printed sheet, which is apparently where he keeps his diary."

        "Ask her yourself. It's her room.":
            $ trait("direct")
            $ rel("noah->player", "respect", 4)
            $ rel("noah->player", "resentment", 2)

            c_noah "It's the school's room."

            narrator "It comes out faster than the rest of him, and he hears it."

            c_noah "That was a rubbish thing to say. I've asked her four times, I'll ask her a fifth, that's fine."

            c_noah "I'd just rather not be the person who keeps turning up."

            c_me "You are the person who keeps turning up."

            c_noah "Yeah."

            narrator "He laughs, properly, at his own expense, and it is the most likeable thing he has done."

        "There's a photograph in there that isn't on any list.":
            $ trait("curious")
            $ rel("noah->player", "trust", 4)
            $ rel("iris->noah", "suspicion", 3)
            $ rel("iris->player", "trust", -2)

            narrator "You hear yourself say it and it is already out."

            c_noah "..."

            c_noah "Okay."

            narrator "He does not write it down, which you notice, and which could mean four different things."

            c_noah "I'm not going to pretend I'm not interested. I am extremely interested."

            c_noah "I'm also going to tell Iris you told me, because otherwise she finds out in a month and it's worse."

            c_me "You don't have to do that."

            c_noah "I do, though."

            narrator "He is right, and it does not help."

    $ learn("noah_is_writing_about_the_archive", source="he_told_me")

    hide noah with dissolve

    return


label s32_st_noah_evening_layout:

    scene bg classroom_2b evening with fade

    narrator "The paper is put together in 2-B on a laptop with a cracked hinge, on the evenings when nobody has booked the room, which is all of them."

    show noah school_summer neutral at s32_centre with dissolve

    c_noah "Column's short. It's always the third column."

    narrator "There are back issues fanned across two desks, in date order, held down with a stapler and somebody's forgotten calculator."

    c_noah "I was going to do a thing where I quote an old issue. Nice, cheap, fills eight centimetres."

    show noah school_summer concerned

    c_noah "The bound volumes are missing a run. Somewhere in the middle. Whole stretch just isn't in the box."

    menu:
        "Doesn't that bother you?":
            $ trait("skeptical")
            $ rel("noah->player", "respect", 2)

            c_noah "Not really?"

            c_noah "They've been in four rooms since anybody bound them. The library moved in — I want to say ninety-eight. Things go missing when things move."

            narrator "He says it without any particular emphasis, and goes back to the column."

            c_noah "Mostly it bothers me because I now have to write eight centimetres myself."

        "Give me half the desks. I'll sort them.":
            $ trait("gentle")
            $ rel("noah->player", "familiarity", 4)
            $ rel("noah->player", "dependency", 2)

            c_noah "Seriously? Right — take those, they go oldest at the bottom, don't trust the dates on the covers, half of them are wrong."

            narrator "You sort papers for twenty minutes. He talks the entire time, about the layout, about a teacher, about a bin fire in the third year."

            c_noah "This is the most help I've had since I started doing this."

            narrator "He says it lightly. It does not sound like it was meant lightly."

        "[trait_label('curious')] How long a run is missing?" if has_trait("curious"):
            $ trait("curious", 2)
            $ rel("noah->player", "trust", 2)
            $ rel("noah->player", "suspicion", 1)

            c_noah "Dunno. A year, near enough."

            narrator "He checks, because he is the sort of person who checks."

            c_noah "Yeah, about a year."

            # Guarded: the player has only heard of another year-long gap if
            # June's booklet or Mara's road walk actually happened. Roughly a
            # third of runs reach this scene without either.
            if knows("school_history_skips_a_year") or knows("mara_knows_the_older_story"):

                c_me "That's the second gap about a year long I've heard about this week."

                c_noah "Is it?"

                narrator "He considers this for exactly as long as it deserves."

            else:

                c_me "A year is a strange amount to lose."

                c_noah "Is it?"

                narrator "He considers this for exactly as long as it deserves."

            c_noah "It's a small school and it's had one bad flood and about six reorganisations. If you go looking for missing years you'll find missing years."

            c_noah "Doesn't mean there's nothing in it. Just means it's cheap evidence."

            narrator "He turns back to the column. Whether that was a reporter being rigorous or a person who has already decided not to look, you could not say from here."

    hide noah with dissolve

    return
