# PROTOTYPE / NON-FINAL
#
# The east hallway. Scene cards: docs/narrative-design/scene-cards/MILESTONE_2.md
#
# 45,280 selection moments happened here in the afternoon in the Milestone 1
# baseline with nothing authored at that hour at all.
#
# `hallway_after_bell` is a group scene and it is the one that has to stay
# ordinary hardest: two people stopping talking when a third arrives is the most
# over-read image in the genre, and here it is exactly what it looks like.
#
# Effects are declared in data/storylets/hallway_*.json.

label s32_st_hallway_lost_property:

    scene bg hallway_east day with dissolve

    narrator "The lost property is a crate. It has been a crate for long enough that the word box has stopped being used about it."

    show theo school_summer neutral at s32_centre with dissolve

    narrator "Theo has it out from under the stairs and he is going through it in layers, taking things out and putting them on the floor in an order that is clearly an order."

    c_theo "Left is checked. Right is not checked. Don't help by putting things back."

    c_me "I wasn't going to help."

    c_theo "People say that and then they tidy."

    menu:

        "Take the right-hand pile.":
            $ trait("gentle")
            $ rel("theo->player", "familiarity", 3)

            narrator "You work through it. Nine unmatched gloves. A recorder. A tie so old the school does not use that pattern any more. A single boot."

            c_theo "The boot's been in there since I got here."

            c_me "Somebody went home with one boot."

            c_theo "Somebody went home with one boot, and never came back for the other one, and that is the part I can't get past."

            narrator "He turns it over twice and puts it back on the checked side, where it does not belong, and does not correct it."

        "What are you actually looking for?":
            $ trait("curious")
            $ rel("theo->player", "respect", 2)

            c_theo "Anything brass."

            narrator "He does not look up. He goes through four more items at the same speed, and then, because you have not filled the pause, he answers it properly."

            c_theo "It's the second time I've done this crate. I know it's not in here. I'm doing it because doing it is better than the alternative, which is deciding it's gone."

            narrator "He says this while holding a swimming cap, which takes some of the weight out of it, and he seems aware of that."

    hide theo with dissolve

    return


label s32_st_hallway_after_bell:

    scene bg hallway_east day with dissolve

    narrator "Mara and June are by the window at the turn of the stairs, mid-sentence, and the sentence stops when you come round the corner."

    show mara school_summer neutral at s32_left with dissolve
    show june school_summer neutral at s32_right with dissolve

    narrator "It stops the way sentences stop, not the way sentences stop in a story about a school. Somebody was asking for something and now there is a third person present."

    c_june "Oh — hi."

    c_mara "..."

    c_june "We're not doing anything sinister. She's got a car."

    show mara school_summer neutral_blush

    c_mara "My mother has a car."

    c_june "Your mother has a car and you have a mother, which between you is a lift."

    narrator "Mara does not agree to this. She also does not say no, and the not-saying-no has been going on long enough that June has started treating it as terms."

    menu:

        "Stay where you are and say nothing.":
            $ trait("reserved")
            $ rel("mara->player", "respect", 3)
            $ rel("june->player", "familiarity", 2)
            $ promise("saturday_with_june", "june", 3, 50)

            narrator "You lean on the rail. June makes the case twice more, in slightly different words, and Mara lets both versions finish."

            c_mara "I'll ask."

            c_june "That's a yes."

            c_mara "It's an ask."

            narrator "June takes it as a yes, and then turns round and includes you in it in the same movement, without asking whether you wanted including."

            c_june "Saturday, then. Half nine at the gate, all four of us."

            narrator "Mara looks at you on the way past, briefly, and you have the strong sense that the look was about being watched rather than about being helped."

        "Sounds like she's already said no twice.":
            $ trait("gentle")
            $ rel("june->player", "trust", 3)
            $ rel("mara->june", "familiarity", 2)
            $ promise("saturday_with_june", "june", 3, 50)

            c_june "She has not said no once, is the thing."

            c_mara "That's true."

            narrator "It lands better than it should. June laughs, and Mara does something with her mouth that is not quite the same thing but is in the same family."

            c_mara "I'll ask her tonight. Stop doing the face."

            c_june "I don't have a face."

            c_mara "You've got several."

            c_june "Saturday. Half nine at the gate. You're coming, you've been here two weeks and you've seen a road and a shop."

            narrator "This is true and is delivered as though it were a diagnosis."

        "What were you talking about?":
            $ trait("direct")
            $ rel("june->player", "familiarity", 4)
            $ rel("mara->player", "suspicion", 3)
            $ rel("mara->june", "suspicion", 2)

            c_june "A lift into town on Saturday. That's genuinely it."

            narrator "June tells you the whole thing, at length, cheerfully, because June answering a direct question is the easiest thing in the building."

            c_mara "..."

            narrator "Mara says nothing at all for the length of it, and then says nothing at the end of it, and leaves before June has finished being reasonable."

            c_june "She's fine. She does that."

            narrator "Which is the entire explanation anybody offers about Mara, and it is offered in the same tone every time, and it explains nothing."

            c_june "We're going into town Saturday, by the way. I'd say come, but I'm going to have to un-ask her about the car first."

            narrator "She says it pleasantly. The invitation does not survive the sentence it arrived in, and both of you notice."

    hide mara with dissolve
    hide june with dissolve

    return
