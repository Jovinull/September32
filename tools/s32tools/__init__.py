"""Development tooling for September 32.

Nothing in this package ships with the game. It exists to keep the authored
content honest: schema generation and validation, headless simulation, coverage
and graph reports, asset acquisition with licence evidence, and credit
generation.

The split from :mod:`s32_engine` is load-bearing. The engine must be importable
by Ren'Py, which cannot install wheels, so it is standard-library only. This
package is free to depend on ``jsonschema``, ``Pillow`` and anything else that
earns its place, and it imports the engine -- never the other way round.
"""

from s32tools.paths import repo_root

__all__ = ["repo_root"]
