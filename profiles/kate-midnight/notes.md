# Kate Midnight — Sound card

## Identity

- Genre: warm piano pop
- Voice: expressive female
- Core trio: acoustic piano, rounded bass, light drums
- Feel: lyrical memorable melody, unhurried phrasing, 88 BPM

## Persistent style prompt

See `version` + `style` in `profile.json`. This string is injected verbatim
into every request; per-song nuances go in `--variation`, not here.

## Using her

New song:

```bash
python agency/generate_from_profile.py kate-midnight \
  --lyrics-file path/to/lyrics.txt \
  --output outputs/kate-song
```

Per-song nuance (appended to the base style):

```bash
... --variation "dark jazz ballad, no piano, 72 BPM"
```

## Evolution rules

- Keep `profile.json` stable while producing a song so a single version maps
  to one sound.
- When her sound changes deliberately, update `style`/`identity`, bump
  `version` to `v2`, and log what changed below.
- Every generated run records `profile_sha256` and `profile_version` in
  `profile_record.json` inside the output directory.

## History

- **v1** (2026-09-19): initial profile derived from `examples/song.json`
  (city_lights).