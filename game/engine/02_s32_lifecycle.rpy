# Lifecycle hooks.
#
# Ren'Py calls these labels at defined moments. Keeping them in one small file
# rather than scattered through the engine bridge makes it obvious what runs
# outside the player's control.

label after_load:
    # A save written by an older build may predate content that now exists.
    # Migrating here — before the scene resumes — means a scene never has to
    # defend itself against a state shape it does not recognise.
    $ s32_after_load()
    return


label splashscreen:
    # Deliberately minimal. A splash is time taken from the player; this one
    # only states what the build is, because shipping a prototype that does not
    # say it is a prototype is how prototypes get reviewed as games.
    scene black
    with Pause(0.2)
    show text "{size=+4}September 32{/size}\n{size=-8}prototype build — not final content{/size}" with dissolve
    with Pause(1.6)
    hide text with dissolve
    with Pause(0.3)
    return


label quit:
    # Nothing is written anywhere on quit. This game has no telemetry and no
    # network access at all; see docs/legal/PRIVACY.md.
    return
