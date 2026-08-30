# tools/reports/

Generated output. Regenerate rather than edit.

```bash
uv run s32 report                # validation, simulation, coverage, graph
uv run s32 assets audit          # character-art consistency
uv run s32 assets sheets         # contact sheets
```

| Path | Committed | |
| --- | --- | --- |
| `character_asset_audit.md` | **yes** | Measurements. The decisions live in `docs/production/CHARACTER_ASSET_AUDIT.md`. |
| `simulation/` | no | Reachability, dead ends, content mix. |
| `coverage/` | no | What exists, in what state, using which parts of the condition language. |
| `graph/` | no | Mermaid and Graphviz exports of the information graph. |
| `contact-sheets/` | no | Derivative images of third-party art — same redistribution restriction as the originals. |

The uncommitted ones are cheap to regenerate and would otherwise produce a diff
on every run.
