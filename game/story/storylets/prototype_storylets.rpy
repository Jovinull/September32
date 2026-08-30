# PROTOTYPE / NON-FINAL
#
# The scenes the director chooses between. Metadata — requirements, effects,
# priority, cooldown — lives in data/storylets/*.json; this file is only the
# writing, which is the split that lets a writer work here without reading any
# JSON and lets the tooling check everything without reading any prose.
#
# Effects are NOT applied here. The director applies them after the label
# returns (see s32_play_effects), so that a rollback past a scene also rolls
# back its consequences. The exception is a choice made *inside* a scene, whose
# effect depends on what the player picked and therefore has to be written here.

label s32_st_archive_intro:

    scene bg archive_room day with dissolve
    show iris school_summer neutral at s32_centre with dissolve

    c_iris "Box seventeen. It's been box seventeen for three weeks."

    c_iris "Every time I open it I find one more thing that isn't on the list, and then it's a different box."

    narrator "The list is a photocopy of a typed list. Somebody has corrected it in pencil, twice, in two different hands."

    c_iris "Anyway. You take the left wall, I'll keep fighting with this."

    show iris school_summer talk

    c_iris "Here — this is what a finished one looks like. Box twelve. Somebody did it properly in about 1990 and then everybody stopped."

    $ s32_open_document("accession_record_box_17")

    hide iris with dissolve

    narrator "The left wall smells like paper that has been warm for a long time."

    return


label s32_st_hallway_encounter:

    scene bg hallway_east day with dissolve
    show theo school_summer neutral at s32_right with dissolve

    c_theo "Archive."

    c_me "That's not my name."

    c_theo "It's what's on the rota."

    narrator "He has a folder under one arm and the specific posture of somebody who has been told they are not allowed to run in the corridor."

    c_theo "If Iris gives you anything without an accession number, don't put it back."

    c_me "Why not?"

    c_theo "Because then it's in the box, and the box says it isn't."

    narrator "He is already walking."

    hide theo with dissolve

    return


label s32_st_old_photo_glimpse:

    scene bg archive_room day with dissolve

    narrator "Box seventeen, second layer down. Between a bundle of sports-day programmes and something that used to be an elastic band."

    show iris school_summer neutral at s32_left with dissolve

    c_iris "Oh, that one."

    c_iris "That one's not on any list. I've checked three."

    narrator "A class photograph. Forty-odd faces in three rows, the back row on a bench, everybody squinting."

    narrator "No names on the back. No year. Somebody has stamped it, once, in the corner, and the ink has gone brown."

    menu:
        "Turn it over properly.":
            $ trait("curious", 2)
            $ rel("iris", "trust", 3)
            narrator "The stamp is a date. Most of it has survived."
            narrator "You get as far as the month before Iris takes it out of your hands, gently, the way you take something from someone who is about to smudge it."
            c_iris "Gloves. Sorry. I'm not being precious, it's the oil on your fingers."
            $ suspect("photo_dated_sept_32", source="a_glance_at_the_stamp")

        "Put it in the maybe pile.":
            $ trait("reserved")
            $ rel("iris", "respect", 3)
            c_iris "Good. That's the correct answer and nobody ever gives it."
            narrator "The maybe pile is four inches deep and growing."

        "Ask who's in it.":
            $ trait("empathetic")
            $ rel("iris", "familiarity", 4)
            c_iris "No idea. That's the problem with the good ones."
            c_iris "Forty people and not one of them wrote anything down."
            narrator "She looks at it a moment longer than the sentence needed."

    show iris school_summer talk

    c_iris "Card first. Everything gets a card, even the things that shouldn't exist yet."

    narrator "She writes the card while you hold the photograph, and she writes it properly, which takes four minutes you had not budgeted for."

    # The photograph is in the player's hands right now, in the prose. The
    # storylet declares `item(old_photo)` too and the director applies it after
    # this label returns; taking it here as well is idempotent and makes the
    # state true at the moment the writing says it is, which is what the
    # document's unlock condition asks about.
    $ take("old_photo")

    # The card's own effects are declared in
    # data/documents/photograph_card_unlisted.json and applied by the engine on
    # first reading — not by this call, and not by a screen action.
    $ s32_open_document("photograph_card_unlisted")

    hide iris with dissolve

    return


label s32_st_message_after_class:

    scene bg classroom_2b day with dissolve

    narrator "There is a folded note in your pigeonhole, which is a thing this school still has."

    c_document "Ledger vol. III, archive rm, tomorrow after fourth. Bring the unlisted photo. — T."

    narrator "It is written on the back of a printed spreadsheet row. The row has been highlighted."

    menu:
        "Fold it up and keep it.":
            $ trait("curious")
            $ rel("theo", "familiarity", 2)
            narrator "You put it in the same pocket as everything else you have not decided about."

        "He could have just asked.":
            $ trait("sarcastic")
            $ rel("theo", "respect", -1)
            $ rel("theo", "familiarity", 2)
            narrator "He could have. He has instead produced a document, which tells you something about Theo."

    return


label s32_st_rain_after_school:

    scene bg rooftop evening with fade

    narrator "The rooftop door does not lock. Half the school knows this and nobody says it out loud, which is its own kind of agreement."

    show iris school_summer neutral at s32_centre with dissolve

    c_iris "You're not supposed to be up here."

    c_me "Neither are you."

    c_iris "No. But I've been not supposed to be up here for longer."

    narrator "Rain, the thin kind that does not commit. She has a camera she is not using."

    c_iris "Can I tell you something that makes me sound strange?"

    menu:
        "Go on.":
            $ trait("empathetic")
            $ rel("iris", "trust", 4)
            c_iris "I photograph things before I catalogue them. Everything. Even the things that turn out to be nothing."
            c_iris "There's a folder on my laptop with about nine thousand photographs of objects nobody has ever asked about."

        "That's a low bar around here.":
            $ trait("sarcastic")
            $ rel("iris", "familiarity", 4)
            $ rel("iris", "attraction", 2)
            narrator "She laughs, once, mostly through her nose."
            c_iris "Fine. I photograph everything before I catalogue it. Everything. Including the nothing."

    c_iris "Because once something's on the list it stops being what it was. It becomes a line."

    c_iris "So I keep the before."

    narrator "The rain gets slightly more serious about itself."

    menu:
        "Show me the folder sometime.":
            $ trait("curious")
            $ rel("iris", "trust", 4)
            $ rel("iris", "attraction", 3)
            c_iris "Maybe."
            narrator "Which from Iris appears to mean yes, eventually, on a day she chooses."

        "That's a lot of photographs of nothing.":
            $ trait("skeptical")
            $ rel("iris", "trust", 1)
            $ rel("iris", "suspicion", 2)
            c_iris "It is."
            c_iris "I'd rather have nine thousand photographs of nothing than one missing photograph of something."

    hide iris with dissolve

    return


label s32_st_courtyard_small_talk:
    # Deliberate filler, lowest priority in the set. Its job is to make an
    # ordinary day feel like a day and not like a queue of plot. Three variants
    # so that repeats do not read as a loop.

    scene bg courtyard day with dissolve

    $ _s32_variant = s32_rng().randint(1, 3)

    if _s32_variant == 1:
        narrator "Somebody is failing to teach somebody else a card game at the far end of the courtyard. It has been the same hand for twenty minutes."
    elif _s32_variant == 2:
        narrator "The vending machine takes your coin and thinks about it. You have started to find this endearing, which is a bad sign about the week."
    else:
        narrator "Two crows are having an argument on the bike rack. Neither is winning."

    narrator "It is the kind of afternoon that will be impossible to remember specifically, later."

    return


label s32_st_theo_ledger_question:

    scene bg archive_room day with dissolve
    show theo school_summer neutral at s32_right with dissolve

    c_theo "You came."

    c_me "You left a note in a pigeonhole. It felt binding."

    narrator "He has the ledger open already, volume three, and a ruler holding the page flat."

    c_theo "Every item in every box gets an accession number, and every accession number gets a date."

    c_theo "That's the whole system. It's not sophisticated, it just has to be complete."

    show theo school_summer concerned

    c_theo "Look at this column."

    narrator "Ruled, numbered, filled in. Fourteen entries in the same hand as the ones above it."

    narrator "There is no date written above it."

    c_theo "Every other column on this page has a date. Every other page has a date on every column."

    menu:
        "Someone forgot.":
            $ trait("skeptical")
            $ rel("theo", "respect", 2)
            c_theo "That was my first answer too."
            c_theo "Then I checked the other two volumes. Ninety-one pages. Nobody has ever forgotten."

        "What's in the column?":
            $ trait("curious", 2)
            $ rel("theo", "trust", 3)
            c_theo "Fourteen items. Eleven of them are in box seventeen."
            c_theo "Two are in the maybe pile."
            c_theo "One is a photograph."
            narrator "You are aware of the shape of your own pocket."

        "Does Iris know?":
            $ trait("direct")
            $ rel("theo", "familiarity", 3)
            $ rel("theo", "suspicion", 2)
            c_theo "..."
            c_theo "Iris photographs things before she catalogues them."
            c_theo "I don't know what that means yet either."
            $ npc_learns("iris", "attendance_sheet_anomaly", "suspected")

    c_theo "I'm not saying it's anything. I'm saying it's not nothing, and those are different."

    c_theo "Look at it yourself. I'd rather you didn't take my word for it."

    # Same reason as above: the ledger is open on the desk in front of the
    # player before the storylet's declared effects run.
    $ learn("attendance_sheet_anomaly", source="theo_showed_me")

    $ s32_open_document("ledger_iii_page_forty")

    hide theo with dissolve

    return
