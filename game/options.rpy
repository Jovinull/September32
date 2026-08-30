## September 32 — project configuration
##
## Values here are the ones this project actually decided. Where a setting is
## Ren'Py's default and we agree with it, it has been removed rather than
## restated: a file of restated defaults hides the handful of choices that were
## made on purpose.

define config.name = _("September 32")

define gui.show_name = True

## Must equal s32_engine.version.GAME_VERSION. `define` is evaluated before any
## `init python` block runs, so the engine cannot be imported here; the literal
## is kept honest by tests/test_version_consistency.py instead, which fails CI
## if the two drift.
define config.version = "0.1.0-prototype"

define gui.about = _p("""
September 32 — prototype build.

This is development infrastructure, not a finished game. The scenes present are
here to exercise the storylet engine, not to tell the story.

Third-party art, music and fonts are used under their own licences. See the
Credits screen and THIRD_PARTY_NOTICES.md.
""")

## Build name. Must not contain spaces or non-ASCII: it becomes a directory and
## archive name on three platforms.
define build.name = "September32"


## Sounds and music ############################################################

define config.has_sound = True
define config.has_music = True
define config.has_voice = False

## The main menu track is set in game/engine/00_s32_engine.rpy, not here:
## `define` is evaluated before any import and so cannot ask whether the file
## exists. Assets are fetched per-developer, and a missing one must never be the
## reason a new contributor cannot start the game.


## Transitions #################################################################
##
## Kept slow and plain on purpose. See docs/style/VISUAL_DESIGN_SYSTEM.md: this
## game's unease comes from things being subtly wrong, and a busy transition
## vocabulary spends the attention that needs to be available for that.

define config.enter_transition = Dissolve(0.3)
define config.exit_transition = Dissolve(0.3)
define config.intra_transition = Dissolve(0.2)
define config.after_load_transition = None
define config.end_game_transition = Dissolve(0.6)


## Window management ###########################################################

define config.window = "auto"
define config.window_show_transition = Dissolve(0.2)
define config.window_hide_transition = Dissolve(0.2)


## Preferences defaults ########################################################

default preferences.text_cps = 0
default preferences.afm_time = 15


## Save directory ##############################################################
##
## An explicit, versioned save directory. Renaming this orphans every player's
## saves, so it is fixed now, before there are any players to orphan.

define config.save_directory = "September32-1"


## Window icon #################################################################

define config.window_icon = "gui/window_icon.png"


## Localisation ################################################################
##
## English is the source language. Internal identifiers — labels, storylet ids,
## knowledge ids — stay in technical English regardless of translation, so that
## a translated build and the tooling still agree about what a scene is called.
## See docs/production/LOCALIZATION.md.

define config.language = None


init python:

    ## Build configuration ####################################################
    ##
    ## Development-only material is excluded from every distribution. The
    ## classify rules run in order, first match wins.

    build.classify("**~", None)
    build.classify("**.bak", None)
    build.classify("**/.**", None)
    build.classify("**/#**", None)
    build.classify("**/thumbs.db", None)

    ## Documentation the player should receive alongside the game. The licence
    ## notices are not optional: several bundled components require them.
    build.classify("game/credits.txt", "all")
    build.documentation("*.html")
    build.documentation("*.txt")

    ## Testcases are developer tooling and must not ship.
    build.classify("game/testcases/**", None)
    build.classify("game/**/*_dev.rpy", None)

    ## Archive the game's own scripts and assets.
    build.classify("game/**.rpy", "archive")
    build.classify("game/**.rpyc", "archive")
    build.classify("game/images/**", "archive")
    build.classify("game/audio/**", "archive")
    build.classify("game/gui/**", "archive")
