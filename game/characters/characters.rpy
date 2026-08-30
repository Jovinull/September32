# The speaking cast.
#
# Ren'Py `Character` objects and the story's `data/characters/*.json` records are
# two halves of the same thing: this file owns how a name is *presented*, the
# JSON owns who the character *is* and which sprite currently plays them.
#
# Colours are chosen to be distinguishable at a glance and to survive the
# archive-paper palette in docs/style/VISUAL_DESIGN_SYSTEM.md. They are not
# character traits; nothing in the writing should depend on them.

define c_iris   = Character("Iris",     color="#7c5c8a", who_prefix="", image="iris")
define c_theo   = Character("Theo",     color="#3f6f8f", image="theo")
define c_mara   = Character("Mara",     color="#8a5c47", image="mara")
define c_june   = Character("June",     color="#4a7a5e", image="june")
define c_noah   = Character("Noah",     color="#8a7a3f", image="noah")

# No sprite yet — see docs/production/ART_GAP_ANALYSIS.md. She still speaks;
# an art gap must never be a reason a character cannot be written.
define c_ellery = Character("Ms. Ellery", color="#5a5a66")

# The protagonist. Unnamed for now: whether they are a defined character or a
# named blank is an open question (docs/canon/OPEN_QUESTIONS.md), and writing
# around it costs nothing today.
define c_me = Character(None)

# Narration attributed to nobody. Used for the protagonist's interiority, which
# in this game is the difference between "a door" and "a door that was open
# yesterday".
define narrator = Character(None, what_italic=False)

# Archive documents speak in their own voice: flat, administrative, and
# unreliable. Styled in game/screens/archive.rpy.
define c_document = Character(
    None,
    what_font="gui/vendor/fonts/SourceSerif4-Regular.ttf",
    what_italic=True,
    what_color="#4a4640",
)
