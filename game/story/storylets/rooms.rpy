# PROTOTYPE / NON-FINAL
#
# 2-B before the bell, and two scenes in the archive. Scene cards:
# docs/narrative-design/scene-cards/MILESTONE_2.md
#
# The two archive scenes are here for competition rather than for mystery. The
# room already had the most content in the game; what it did not have was a
# reason to be in it that was not the plot. `archive_iris_index` uses the
# document viewer a second time, which is the point of having built it.
#
# Effects are declared in data/storylets/classroom_before_bell.json and
# data/storylets/archive_*.json.

label s32_st_classroom_before_bell:

    scene bg classroom_2b day with dissolve

    $ _v = s32_rng().randint(1, 2)

    if _v == 1:

        narrator "The chairs are still on the desks from the cleaners and the radiator is doing the thing where it is hot at one end and cold at the other."

        narrator "Somebody has left a piece of homework on the third desk from the window. It has a name on it and a mark on it and neither is anything to do with you, and you turn it face down, which is either courtesy or interference."

        narrator "The room smells of the polish they use on Mondays. It is a good smell and you would not say so out loud."

    else:

        show june school_summer neutral at s32_centre with dissolve

        narrator "June is already in, chairs already down, sitting on a desk rather than at one."

        c_june "I get in early. It's not virtue, I just can't do the corridor at half eight."

        c_me "That's fair."

        c_june "It is fair. Everyone acts like it's a personality thing."

        narrator "She takes the chairs down off two more desks while she is talking, without appearing to notice she is doing it, and by the time the bell goes she has done the whole row."

        hide june with dissolve

    return


label s32_st_archive_iris_index:

    scene bg archive_room day with dissolve

    narrator "Iris has a shoebox on the desk, and the shoebox is full of cards, and the cards are handwritten."

    show iris school_summer neutral at s32_centre with dissolve

    c_iris "You can look. It's not a secret, it's just not official."

    narrator "Each card is a box number, a rough description, and a date range with a question mark after it more often than not."

    c_iris "The accession record is the official one. It's in the cabinet, it's leather, it's beautiful, and you cannot find anything with it."

    c_me "Why not?"

    c_iris "Because it records the order things arrived in. Not what they are."

    # A second, different reason to open a document the player may already have
    # read. The viewer applies its effects once; re-reading is deliberately free.
    $ s32_browse_document("accession_record_box_17")

    c_iris "That's a real page. Box seventeen. Tell me what's in box seventeen."

    c_me "It says received."

    c_iris "It says received."

    narrator "She puts the card for box seventeen on the desk next to it. The card says {i}photographs, loose, mixed, 1950s?{/i}"

    menu:

        "I could help you keep it up.":
            $ trait("gentle")
            $ rel("iris->player", "trust", 4)
            $ rel("iris->player", "attraction", 2)

            c_iris "You'd get bored."

            c_me "Probably."

            c_iris "..."

            c_iris "There's a second shoebox. It's not started."

            narrator "She does not hand it to you. She moves it about four inches closer, which given the last three weeks is enormous."

        "The office would take that off you if they knew.":
            $ trait("skeptical")
            $ rel("iris->player", "respect", 3)
            $ rel("iris->player", "resentment", 2)

            c_iris "Yes."

            narrator "She says it without any of the heat you were braced for, and puts the lid on the box, and the lid going on is the whole reply."

            c_iris "They'd take it, they'd say it wasn't procedure, and then in four years somebody would start one again from nothing."

            c_iris "I'd rather do the four years now."

        "What do you think isn't in the box?":
            $ trait("curious")
            $ rel("iris->player", "trust", 2)
            $ rel("iris->player", "respect", 3)

            c_iris "That's a better question than the one people usually ask."

            c_iris "The cards are what I've found. The record is what arrived. They don't match, and they've never matched, and everyone senior than me is fine with that because the record balances."

            c_me "So things arrived and aren't here."

            c_iris "Or they're here and never arrived. It's a school store cupboard with a leather book in it. It isn't the Bodleian."

            narrator "She is careful, and she is careful in a way that is about not overstating, which is a different thing from being evasive."

    hide iris with dissolve

    return


label s32_st_archive_theo_returns:

    scene bg archive_room day with dissolve

    narrator "Theo is in the doorway of the archive, which is as far as he has got."

    show iris school_summer neutral at s32_left with dissolve
    show theo school_summer neutral at s32_right with dissolve

    c_theo "I'm not asking to look at anything. I'm asking whether anybody handed one in."

    c_iris "And I'm telling you nobody has handed anything in, because I'd have it."

    c_theo "You'd have it in the box, or you'd have it written down?"

    show iris school_summer concerned

    c_iris "Both. That's the whole point of me."

    # The one place an NPC-to-NPC edge is visible to the player. `iris->theo`
    # suspicion comes from this scene's own first branch on a previous run, and
    # from `annexe_two_of_them`; `theo->iris` respect comes from the common
    # room. The player did not make either of these and can see both.
    if rel_get("iris->theo", "suspicion") >= 3:

        narrator "It is not an argument yet, and it is not the first time. They have the specific efficiency of two people who have already had the general version and are now doing the particular one."

    elif rel_get("theo->iris", "respect") >= 3:

        narrator "It is not an argument. It is two people being precise at each other, both correctly, and Theo is being careful in a way he is not careful with anyone else in this building."

    else:

        narrator "It is not an argument yet. It is two people being precise at each other, both correctly, which is the stage immediately before an argument."

    c_theo "It's a brass key. It opens the annexe cupboard and I'm supposed to have it and I don't."

    c_iris "Then it's not in this room."

    menu:

        "She would know. She keeps two records.":
            $ trait("direct")
            $ rel("iris->player", "trust", 3)
            $ rel("theo->player", "respect", -1)
            $ rel("iris->theo", "suspicion", 2)

            c_theo "Right."

            narrator "He does not say the thing he is thinking, and he takes slightly too long not to say it, which comes to the same."

            c_theo "Then I'll try the office."

            narrator "Iris watches the doorway for a moment after he has gone, and then goes back to the desk, and does not mention it again."

        "He is not accusing you of anything.":
            $ trait("gentle")
            $ rel("theo->player", "trust", 3)
            $ rel("iris->player", "familiarity", 2)
            $ rel("theo->iris", "respect", 2)

            c_iris "I know he isn't."

            narrator "She says it in a tone that establishes she had not, in fact, known that."

            c_iris "Sorry. It's — people come in here twice a term and both times it's because something's missing, and I'm the person the room belongs to."

            c_theo "That's fair. I'd be the same about the ledger."

            narrator "Which is, you notice, an odd thing for him to have compared it to."

        "Say nothing.":
            $ trait("reserved")
            $ rel("iris->player", "respect", 2)
            $ rel("theo->player", "respect", 2)
            $ rel("iris->theo", "familiarity", 2)

            narrator "You stay out of it and it resolves itself in about ninety seconds, the way most of these do."

            c_iris "If it turns up I'll put it aside."

            c_theo "Thanks. Sorry to come at you with it."

            c_iris "You didn't come at me with anything."

            narrator "They are both slightly nicer to each other by the end of it than they were at the start. Nobody added anything, and that turns out to have been the whole job."

    hide iris with dissolve
    hide theo with dissolve

    return
