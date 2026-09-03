init -100 python in gui:

    def scale(n):
        return int(n)

init 100 python in gui:

    # Regenerating the GUI bitmaps at the project's resolution, when and only
    # when the SDK is present.
    #
    # `gui7` lives in the SDK's launcher and is not part of a distribution. An
    # unguarded import crashes a built game before the main menu, which is how
    # the first playtest build failed its fresh-install test -- the guard is
    # the whole reason a build gets unpacked somewhere else and run there.
    #
    # A built game does not need this. `s32 assets install` and
    # tools/s32tools/renpy_gui_scale.py leave the committed bitmaps already at
    # 1920x1080, and this block only ever overwrote them with the same thing.

    if not renpy.mobile:
        from store import config

        import sys
        import os

        _launcher = os.path.join(config.renpy_base, "launcher", "game")

        if os.path.isdir(os.path.join(_launcher, "gui7")):
            sys.path.insert(0, _launcher)

            from gui7.parameters import GuiParameters
            from gui7.images import ImageGenerator
            from gui7 import generate_gui

            p = GuiParameters(
                config.gamedir, config.gamedir,
                config.screen_width, config.screen_height,
                accent_color, "#000000", False, None,
                True, False, False, "gui")

            p.skip_backup = True

            generate_gui(p)

            _skip_backup = True
            _gui_images()
