# Scaffolding for the Act 1 golden path, and nothing else.
#
# This file is developer tooling. `build.classify("game/testcases/**", None)` in
# options.rpy keeps the whole directory out of every distribution, which is why
# the overrides below can exist at all: none is reachable from a build a tester
# receives, and none is reachable from normal play.
#
# They exist because of a specific gap. The Ren'Py test language can click a
# named button and can advance a line of dialogue, and a full Act 1 is roughly
# nine hundred lines and fifty menus. Writing that out would produce a test
# nobody could read and that broke on every content edit. What the golden path
# is actually for -- proving that fifty-eight storylet labels and five anchors
# execute in Ren'Py without throwing -- needs the scenes played, not the menus
# clicked, and the menus are covered by the other testcases in this directory.

init 999 python:

    #: The real implementations, captured before anything replaces them.
    _s32_menu_real = menu
    _s32_ask_where_real = s32_ask_where
    _s32_open_document_real = s32_open_document

    def _s32_open_document_headless(document_id):
        """The unlock and first-reading half of s32_open_document, no screen."""
        document = s32_library_documents.documents.get(document_id)
        if document is None:
            raise Exception("no such document: {}".format(document_id))
        if not s32_documents.is_unlocked(S32State, document, s32_rng()):
            return False
        s32_documents.mark_read(S32State, document)
        s32_pt_document(document_id)
        return True

    def s32_test_autochoice(on=True, index=0):
        """Answer every menu with the same option, without an interaction.

        Replaces the store's `menu`, which is the documented hook and the one
        nvl mode uses, and the travel seam beside it. The choice is still
        recorded in the playtest report, so the golden path exercises that
        path too.

        `index` is the position among the options actually offered, so a menu
        whose first option is conditioned out still gets a valid answer.
        """
        global menu, s32_ask_where

        if not on:
            menu = _s32_menu_real
            s32_ask_where = _s32_ask_where_real
            return

        def picker(items, *args, **kwargs):
            choices = [value for _label, value in items if value is not None]
            if not choices:
                return None
            chosen = choices[min(index, len(choices) - 1)]
            value = getattr(chosen, "value", chosen)
            s32_pt_choice(items, value)
            return value

        def where(items):
            return items[min(index, len(items) - 1)][1]

        menu = picker
        s32_ask_where = where

    def s32_test_fast_documents(on=True):
        """Apply a document's effects without opening the viewer.

        The viewer itself is tested properly in archive.rpy, where a person's
        actual interaction with it is what is being checked. Here it would only
        be a modal screen standing between the harness and the next scene.
        """
        global s32_open_document

        s32_open_document = _s32_open_document_headless if on else _s32_open_document_real
