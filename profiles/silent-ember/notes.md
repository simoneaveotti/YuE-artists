# Silent Ember — Sound card

## Chi sono

Quartetto rock essenziale (voce, chitarra, basso, batteria) con un principio:
"Rock e tutto ciò che può derivarne, senza limiti."

Il manuale operativo completo è in **`IDENTITY.md`** in questa cartella. Rileggilo
a ogni sessione; sostituisce qualsiasi ricetta generica sul rock.

## Identità operativa (profilo)

- **`style`** (v1): base parlante del suono — quartetto rock, voce maschile
  espressiva, produzione moderna con dinamica, spazio e grit, apertura a texture
  crude, atmosferiche ed elettroniche.
- **`defaults.language`**: English. I testi in italiano si chiedono brano per
  brano con `--variation "Italian lyrics"`.
- **`operating_brief`**: punta a `IDENTITY.md`.

## Come si lavora con lei

Perché l'identità della band è "senza limiti", **quasi tutta la caratterizzazione
di un brano vive nel `--variation`**, non nel profilo. Il profilo fornisce il
core; la variazione dà la direzione specifica del pezzo.

```bash
python agency/generate_from_profile.py silent-ember \
  --lyrics-file path/to/lyrics.txt \
  --variation "slow-burn post-rock build, huge reverbs, processed vocal layers, no obvious riff" \
  --output outputs/silent-ember-<song>
```

- `--prepare-only` per rivedere la request esatta prima di spendere compute.
- Lo stile usato finisce in `profile_record.json` dentro ogni output, insieme a
  `profile_sha256` e `version`.

## Versioni del profilo

| v | data | cosa cambia |
| --- | --- | --- |
| v1 | 2026-09-19 | Profilo iniziale dal brief della band; lingua default inglese. |

Regola: si aggiorna il profilo quando cambia il suono **della band**, non per un
singolo brano. Un brano si racconta con `--variation`.