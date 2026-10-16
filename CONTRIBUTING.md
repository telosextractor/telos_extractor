# Contributing

## Code conventions

- **English only** in code: names, comments, docstrings, error messages, commit messages.
- **No logic in the entry point.** `main` / CLI only parses input, calls the pipeline
  and prints the result. All domain logic lives in `extraction/` or `rules/`.
- **Money and weights use `Decimal`**, never `float`.
- **Warnings and errors carry codes**, not sentences (e.g. `ARTICLE_NOT_FOUND`).
  Translation into German/English happens only at output (i18n).

## Glossary (German domain term → code)

| German | Code |
|---|---|
| Rechnung | `Invoice` |
| Rechnungsnummer / -datum | `invoice_number` / `invoice_date` |
| Warenwert | `goods_value` |
| Eigenmasse (Netto) | `net_mass` |
| Bruttogewicht | `gross_mass` |
| Artikel | `InvoiceItem` |
| GE EAN | `trade_unit_gtin` |
| Sorte | `Variant` |
| Karton | `cartons` |
| Tarifnummer | `tariff_number` |
| Zollposition | `CustomsPosition` |

## Git workflow

1. `git checkout main && git pull`
2. `git checkout -b feature/<topic>`
3. Commit, then `git push -u origin feature/<topic>`
4. Open a pull request – the other person reviews before merging into `main`.

Never commit real documents or master data (`data/private/`, `*.xlsx`).
