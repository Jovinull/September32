# PROTOTYPE / NON-FINAL
#
# The two locations that had no content: the dorm and the road into town.
# Scene cards: docs/narrative-design/scene-cards/MILESTONE_1.md
#
# `dorm_message` is the milestone's main delayed callback. It reads commitment
# and relationship state and produces a different scene from one file, and every
# reference to an earlier scene is guarded — it must work no matter what the
# player has or has not done.
#
# Effects are declared in data/storylets/dorm_message.json and
# data/storylets/town_road_evening_walk.json.

label s32_st_dorm_message:

    scene bg dorm_room evening with fade

    narrator "The radiator comes on at six whether or not it is cold, and there is no way to argue with it."

    # Guarded throughout: none of these scenes is guaranteed to have happened.
    if s32_commitments.status(S32State, "june_favour") == "active":

        c_document "chairs at 4 thurs. you said yes. this is not pressure it is a reminder that reads like pressure. — J"

        narrator "There is a second line, sent four minutes later, that just says {i}sorry{/i} and nothing else."

        menu:
            "Answer her.":
                $ trait("gentle")
                $ kept("june_favour")
                $ rel("june", "trust", 4)

                narrator "You type {i}I said yes, I'm coming{/i} and delete the {i}I said yes{/i} because it reads as annoyed."

                c_document "ok good. bring a jumper the hall is a fridge"

                narrator "That is the entire exchange and it takes eleven seconds and you feel notably better afterwards, which is embarrassing."

            "Leave it until morning.":
                $ trait("reserved")
                $ broke("june_favour")
                $ rel("june", "resentment", 3)

                narrator "You put the phone face down. It is a reasonable decision made at the reasonable hour of six in the evening."

                narrator "In the morning there is nothing further from her, which is not the same as it being fine."

            "[trait_label('curious')] Look at the photograph again." if has_trait("curious") and has_item("old_photo"):
                $ trait("curious", 2)
                $ rel("iris", "familiarity", 2)

                narrator "You answer June first — {i}coming{/i}, one word — and then take the photograph out of the drawer and put it under the desk lamp."

                $ kept("june_favour")
                $ rel("june", "trust", 4)

                narrator "Forty-odd faces. The bench in the back row is the same bench that is still in the courtyard, which you had not noticed and which is not interesting, exactly."

                narrator "You put it back in the drawer. You are aware that you put it back rather than filing it, and that those are different."

    elif has_item("old_photo"):

        narrator "The photograph has been in your bag all day and you take it out because the desk is the only flat surface in the room that is not the bed."

        menu:
            "Look at it properly.":
                $ trait("curious", 2)
                $ rel("iris", "familiarity", 2)

                narrator "Forty-odd faces. Three rows. The back row is standing on a bench, and it is the same bench that is still in the courtyard, which you had not noticed."

                narrator "Nobody in it is looking at the camera in the same way. That is true of every group photograph ever taken and you sit with it anyway."

            "Put it somewhere safe.":
                $ trait("reserved")

                narrator "The drawer, under the booklet you never read, which is at least dry and dark and flat."

                narrator "Iris would have photographed it first. You are fairly sure she would have photographed it first."

    else:

        narrator "Nothing has arrived. Nobody needs anything. It is six in the evening and the day has simply stopped."

        menu:
            "Get ahead on the reading.":
                $ trait("reserved")
                narrator "You get through eleven pages and remember four of them, which is roughly the usual rate."

            "Sit for a bit.":
                $ trait("gentle")
                narrator "The radiator ticks. Downstairs somebody is failing to make a phone call work."
                narrator "It is not a bad room. It came furnished — somebody else's dent in the mattress, somebody else's mark on the desk where a lamp used to be — but it is not a bad room."

    return


label s32_st_town_road_evening_walk:
    # Deliberately mundane, in three variants. The road's ordinariness is an
    # asset the story spends later, so no variant may end on an ominous line and
    # none of them may foreshadow anything. See the scene card.

    scene bg town_road evening with dissolve

    $ _s32_variant = s32_rng().randint(1, 3)

    if _s32_variant == 1:
        narrator "Somebody has parked a caravan in the layby and left a sign on it saying NOT FOR SALE, which raises more questions than it settles."
        narrator "The hedge has been cut on one side only. You walk to the bend and back."

    elif _s32_variant == 2:
        narrator "The bus into town goes past you with four people on it and one of them waves, and you wave back before working out that you do not know them."
        narrator "It is that kind of road. Everyone waves. Nobody has decided to stop."

    else:
        narrator "There is a postbox at the halfway point with the collection times worn off the plate, and somebody has written them back on in marker."
        narrator "The marker is more recent than the paint and older than you are, and both of those facts are perfectly ordinary."

    return
