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
define config.version = "0.2.0-playtest.1"

## The About text a tester reads. It has to do two jobs at once: say plainly
## that this is a private test of Act 1, and not read as a debug build. See
## docs/production/PLAYTEST_BUILD.md.
define gui.about = _p("""
September 32 — Act 1, private playtest.

This is the first week of the story, given to a small number of people to read
before anything else is written. It ends where Act 1 ends, on purpose.

Some visual assets are temporary and should not be judged as final art. The
class photograph in particular is a placeholder.

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

    ## What the archive and its top-level folder are called. A tester should be
    ## able to tell from the file name alone which build they were sent, six
    ## weeks after they were sent it. The executable keeps the short name.
    build.directory_name = "September32-Act1-Playtest-" + config.version
    build.executable_name = "September32"

    build.classify("**~", None)
    build.classify("**.bak", None)
    build.classify("**/.**", None)
    build.classify("**/#**", None)
    build.classify("**/thumbs.db", None)

    ## Compiled Python caches. Not merely noise: a .pyc embeds the absolute
    ## path of the source file it was compiled from, which on a developer's
    ## machine is a home directory with a name in it. Ren'Py compiles the
    ## engine package itself at first run, so shipping these gains nothing
    ## either.
    build.classify("**/__pycache__/**", None)
    build.classify("**.pyc", None)

    ## Documentation the player should receive alongside the game. The licence
    ## notices are not optional: several bundled components require them.
    build.classify("game/credits.txt", "all")
    build.documentation("*.html")
    build.documentation("*.txt")

    ## Testcases are developer tooling and must not ship.
    build.classify("game/testcases/**", None)
    build.classify("game/**/*_dev.rpy", None)

    ## Authored content, mirrored into the game tree by `s32 build`.
    ##
    ## In development the repository's `data/` sits beside `game/` and the
    ## engine finds it there. A distribution has no repository, so the build
    ## step copies it in. Without this rule the built game loads zero storylets
    ## and the director has nothing to select — which is a silent failure, not
    ## a crash, and therefore worth being explicit about.
    build.classify("game/data/**", "archive")

    ## The build stamp: version, build id and commit, written by `s32 build`
    ## and read back at init so a bug report can name the exact build.
    build.classify("game/build_stamp.json", "archive")

    ## Archive the game's own scripts and assets.
    build.classify("game/**.rpy", "archive")
    build.classify("game/**.rpyc", "archive")
    build.classify("game/images/**", "archive")
    build.classify("game/audio/**", "archive")
    build.classify("game/gui/**", "archive")

    ## Everything else in the repository is internal and must not be handed to
    ## a tester: design documents, canon, briefs, the asset pipeline, the
    ## vendor archives, the tests, the tooling and the reports.
    ##
    ## Two things about how Ren'Py reads these rules, both of which decide the
    ## shape of what follows. **First match wins**, so the three documents a
    ## tester is supposed to receive are classified above the sweep that would
    ## otherwise catch them. And the scan is a walk that does not descend into
    ## a directory it has excluded, so each of these is written as `name/`
    ## rather than `name/**`: the `**` form leaves the directory itself
    ## unmatched and ships an empty folder.
    ##
    ## Ren'Py's own defaults end with a catch-all that sweeps the entire base
    ## directory into the distribution, and the base directory here is a
    ## repository. Without this block a tester would receive the canon, the
    ## briefs, the internal reports and every scene card.
    ##
    ## Held by tests/test_playtest_build.py, which lists the repository root
    ## and fails on an entry no rule here accounts for -- so a directory added
    ## next year is a failing test rather than a leak.
    build.classify("PLAYTEST_README.md", "all")
    build.classify("FEEDBACK_INSTRUCTIONS.md", "all")
    build.classify("THIRD_PARTY_NOTICES.md", "all")
    build.classify("LICENSE", "all")

    build.classify("docs/", None)
    build.classify("tools/", None)
    build.classify("tests/", None)
    build.classify("scripts/", None)
    build.classify("data/", None)
    build.classify("assets/", None)
    build.classify("research/", None)
    build.classify("playtests/", None)
    build.classify("*.md", None)
    build.classify("*.toml", None)
    build.classify("*.lock", None)
    build.classify("*.txt", None)
