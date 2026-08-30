# ADR-0008 — No creator-defined statements, for now

**Status:** Accepted · 2026-08-30

## Context

Ren'Py's `renpy.register_statement` allows custom script syntax. An obvious
application here would be a `storylet` statement carrying metadata and prose
together:

```renpy
storylet iris_rooftop_rain:
    requires "weather == rain", "rel iris.trust >= 10"
    effects "rel iris.trust += 5"

    c_iris "You're not supposed to be up here."
```

That reads well. The question is whether it earns its cost.

## Decision

**Not yet.** The metadata split (ADR-0006) already solves the problem a DSL
would solve, and a DSL would take away things the project depends on.

What is used instead is the ordinary Ren'Py vocabulary plus a small set of
plain Python helpers, defined in `game/engine/00_s32_engine.rpy`:

```renpy
$ rel("iris", "trust", 3)
$ learn("photo_dated_sept_32", source="back_of_the_photo")
$ promise("meet_theo_archive", "theo", in_days=1, importance=60)
```

These are functions, not syntax. Every editor understands them, `renpy lint`
understands them, and a reader can jump to the definition.

## Alternatives

**A full `storylet` statement.** Rejected for four reasons:

1. *It duplicates the JSON.* Metadata would live in two places, or the JSON
   would be generated from the `.rpy`, which means the tooling has to parse
   Ren'Py script — a parser this project would then have to maintain.
2. *It breaks the tooling.* The validator, the reachability checker and the
   simulator all read JSON today, cheaply and reliably. Reading a custom
   statement means reimplementing Ren'Py's parser or booting Ren'Py to
   introspect, and the second option makes the headless simulator impossible.
3. *Editors do not understand it.* Ren'Py syntax highlighting exists; syntax for
   one project's custom statement does not.
4. *It hides logic in magic.* A reader who does not know the DSL cannot read the
   scene. A function call is self-explanatory.

**A tiny `run_storylet "id"` statement.** Genuinely small, and genuinely
unnecessary: `$ renpy.call(storylet.label)` inside the director loop already
does it, once, in one place.

## Consequences

**Good**

- One representation of metadata.
- Tooling stays simple and fast, and works without Ren'Py.
- Standard tooling, standard highlighting, standard lint.

**Bad, and accepted**

- Scene scripts carry a few more `$` lines than a bespoke syntax would.
- Effects are written twice for choice branches: once as prose effects, once as
  declared `outcomes` (ADR-0006).

## Revisit if

Writers report the metadata split as a genuine friction in practice — not in
theory. If they do, the right first step is a small statement that *generates*
the JSON at build time, keeping JSON as the single representation the tooling
reads.
