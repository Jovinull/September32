# PROTOTYPE / NON-FINAL
#
# Mara. Scene cards: docs/narrative-design/scene-cards/MILESTONE_1.md
# Voice: docs/characters/VOICES.md and docs/characters/mara.md
#
# Flat declaratives. Pauses you are meant to notice. Says "here" instead of
# naming the town. States a fact adjacent to the question and stops.
#
# Effects are declared in data/storylets/mara_*.json.

label s32_st_mara_reads_the_room:

    scene bg hallway_east day with dissolve
    show mara school_summer neutral at s32_right with dissolve

    c_mara "Theo's checking the ledger again."

    c_me "How do you know that?"

    c_mara "He goes the long way round when he's carrying it. Past the noticeboard, down the far stairs."

    c_mara "Nobody goes that way. It's four minutes longer."

    narrator "She says it the way you would read out a bus timetable."

    c_mara "He does it so he doesn't have to explain what he's carrying."

    show mara school_summer talk

    c_mara "June eats on her own most days. Second bench, by the bins, which is the worst bench."

    c_me "Does she?"

    c_mara "She's been doing it since about March."

    narrator "There is a pause here, exactly long enough."

    c_mara "I think she's had a falling-out with somebody and hasn't said."

    menu:
        "That sounds about right.":
            $ rel("mara", "familiarity", 3)
            $ rel("june", "suspicion", 2, source="mara")

            c_mara "It usually is."

            narrator "She does not say it smugly. She says it the way you would confirm the time."

        "[trait_label('empathetic')] Or she just likes eating on her own." if has_trait("empathetic", 2):
            $ trait("empathetic")
            $ rel("mara", "respect", 4)
            $ rel("mara", "suspicion", 2)
            $ rel("june", "suspicion", 2, source="mara")

            narrator "Mara stops walking."

            c_mara "..."

            c_mara "Maybe."

            narrator "It is the first thing you have said that she has not had an answer ready for, and she does not enjoy it."

            c_mara "I'd still put money on the falling-out."

            narrator "She starts walking again. She is not annoyed with you. She is annoyed with the possibility."

        "Tell me about Theo instead.":
            $ trait("curious")
            $ rel("mara", "trust", 3)
            $ rel("theo", "respect", 2, source="mara")

            c_mara "Theo's fine."

            c_mara "He'll do a thing properly and then do it again in case he did it wrong the first time. People think that's about the work."

            c_me "It isn't?"

            c_mara "It's about not letting anybody down. It just comes out looking like paperwork."

            narrator "She shrugs, which from Mara is a whole paragraph."

    $ npc_learns("mara", "theo_checks_the_ledger", "known")

    hide mara with dissolve

    return


label s32_st_mara_older_story:

    scene bg town_road evening with fade

    narrator "The road into town has a pavement for about half of it and then stops having one, and everybody walks in the road anyway."

    show mara school_summer neutral at s32_centre with dissolve

    c_mara "You're going the wrong way for the dorms."

    c_me "I'm going the right way for not being in the dorms."

    c_mara "Fair enough."

    narrator "She adjusts her bag and does not offer to walk with you, which turns out to be what walking with you looks like."

    narrator "Two hundred metres of nothing. A gate. A dog that has decided about you already."

    c_mara "Iris found something in a box, then."

    c_me "How did — "

    c_mara "Theo went the long way round twice in one day."

    show mara school_summer neutral_blush

    narrator "You had not said a word about the photograph."

    c_mara "There's a year they didn't print a yearbook. My grandmother was here for it."

    c_mara "There's a version of why."

    menu:
        "Tell me the version.":
            $ trait("curious")
            $ rel("mara", "trust", 2)
            $ rel("mara", "resentment", 3)
            $ suspect("photo_is_a_forgery", source="mara_thinks_someone_faked_it")

            c_mara "No."

            narrator "Flat. Not angry. The pause after it is the longest one yet."

            c_mara "I've got it third-hand off a woman who told it to be entertaining. If I say it out loud to somebody from outside it stops being a family thing and starts being a fact, and it isn't one."

            c_me "That's fair."

            c_mara "It's not fair, it's just what I'm doing."

            narrator "She walks a while."

            c_mara "For what it's worth — somebody could have faked a stamp on a photograph. People did things for a laugh back then same as now."

            c_mara "That's not the version. That's just me being sensible at you."

        "Then I won't ask.":
            $ trait("gentle")
            $ rel("mara", "trust", 5)
            $ rel("mara", "respect", 3)
            $ suspect("photo_is_a_forgery", source="mara_thinks_someone_faked_it")

            c_mara "..."

            c_mara "Thanks."

            narrator "Another hundred metres. The dog has lost interest."

            c_mara "It's third-hand and it was told to be entertaining, which is the problem with all of it."

            c_mara "I'll tell you the boring part. Somebody could have faked a stamp on a photograph. That happens. That has always happened."

            c_mara "I'd rather you had a dull explanation before you go collecting an interesting one."

            narrator "It is the closest thing to a gift she has offered anyone this week and she would deny that flatly."

        "This town is strange about that year.":
            $ trait("direct")
            $ rel("mara", "suspicion", 4)
            $ rel("mara", "trust", -1)

            c_mara "..."

            narrator "She keeps walking at exactly the same speed."

            c_mara "It's a place where about four hundred people live."

            c_mara "One of them didn't print a book once."

            narrator "At the junction she goes right, towards the shops, and you had not established that she was going to the shops."

    $ learn("mara_knows_the_older_story", source="mara_on_the_road")
    $ npc_learns("mara", "old_photo_exists", "suspected")

    hide mara with dissolve

    return
