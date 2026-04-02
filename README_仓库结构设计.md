# Repository Structure Notes

## Design Goal

This project is easier to maintain when:

- text files are the source of truth
- scripts do the calculation and export work
- Excel is used only for review and manual inspection

## Recommended Layout

```text
GCG/
├─ data/
│  ├─ cards/
│  │  └─ cards.yaml
│  ├─ value_tables/
│  │  └─ value_table.yaml
│  ├─ decks/
│  │  ├─ blue_purple_sample_50.txt
│  │  └─ deck_meta.yaml
│  └─ scenarios/
│     └─ p22_blue_purple_sample.yaml
├─ docs/
│  └─ 数据字段说明.md
├─ schemas/
│  ├─ cards.schema.yaml
│  ├─ value_table.schema.yaml
│  ├─ deck.schema.yaml
│  └─ p22_scenario.schema.yaml
├─ output/
├─ archive/
├─ run_p22_greedy.py
├─ export_cards_yaml.py
└─ export_value_table_yaml.py
```

## Why Not Use Excel As Source Of Truth

- poor git diff experience
- hard to review rule changes
- merge conflicts are painful
- data, formulas, and formatting become tightly coupled

## Recommended Maintenance Model

### `cards.yaml`

Stores base card data:

- id
- name
- type
- LV / COST
- AP / HP
- traits
- resonance
- raw effect text

### `value_table.yaml`

Stores effect-value definitions:

- effect name
- parameter names
- output dimensions
- notes

### `decks/*.txt`

Keep decklists readable for players:

```text
// Main Deck
4x ST01-005
4x ST05-004
```

### `scenarios/*.yaml`

Stores simulation settings for P2-2:

- which deck to run
- how many turns to run
- fallback condition probability
- whether resonance is handled exactly

## Output Layer

- generated outputs go to `output/`
- archived spreadsheets and backups go to `archive/`
- both should stay ignored by git
