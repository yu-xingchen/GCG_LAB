# GCG_LAB

`GCG_LAB` is a text-source toolkit for analyzing Gundam Card Game decks.

The current repository is moving away from Excel-as-source and toward:

- structured card data
- structured value-table data
- reproducible simulation scripts
- git-friendly maintenance

## Current Files

- `data/cards/cards.yaml`: exported card data
- `data/value_tables/value_table.yaml`: value table source
- `data/decks/*.txt`: decklists
- `data/scenarios/*.yaml`: simulation scenarios
- `run_p22_greedy.py`: current P2-2 greedy simulator
- `fix_p21_workbook.py`: workbook-side P2-1 cleanup helper

## Current Scope

The repo already supports:

- exporting card data from the workbook
- exporting the value table into YAML
- keeping decklists in text form
- running a starter P2-2 greedy simulation from text data
- cleaning up parts of the P2-1 workbook output

## Project Direction

The intended long-term direction is:

1. keep source data in text files
2. treat Excel as an output / review surface
3. build a GUI for "scientific" GCG deck analysis

## Notes

- old Excel workbooks and backups are ignored by git
- generated output folders are also ignored
- the current simulator is still a starter, not full Excel parity yet
