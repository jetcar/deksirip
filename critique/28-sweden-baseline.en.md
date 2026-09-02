# Baseline calculation: Sweden

## Why this case was chosen

Sweden is a better first test of the model than Norway: it is a small, wealthy, industrially diverse country with strong energy infrastructure and developed foreign trade, but without the same degree of dependence on oil and gas rents.

The calculation does not ask how many people are employed today. It should show how many person-hours are needed for a defined basic standard of living, infrastructure maintenance, and external balance.

## Fixed demographic and labour baseline

Working assumptions and the control scenario are in [calculations/sweden/assumptions.en.md](../calculations/sweden/assumptions.en.md).

According to official Swedish statistics:

- population at the end of 2025 — **10,605,529 people**;
- employed people aged 15–74 in 2025 — **5,263,000 people**;
- average actual hours worked — **156.1 million hours per week**.

The last figure equals approximately **8.12 billion hours per year** and **765 hours of actual work per resident per year**. This is the observed labour volume, not a requirement of the basic system.

Sources: [Statistics Sweden — population](https://www.scb.se/en/finding-statistics/statistics-by-subject-area/population-and-living-conditions/population-composition-and-development/population-statistics/pong/statistical-news/population-statistics-year-2025-publish-1/), [Statistics Sweden — Labour Force Survey 2025](https://www.scb.se/en/finding-statistics/statistics-by-subject-area/labour-market/labour-force-supply/labour-force-surveys-lfs/pong/statistical-news/labour-force-surveys-lfs-2025/), [SCB — employment and hours by industry](https://www.statistikdatabasen.scb.se/pxweb/en/ssd/START__AM__AM0401__AM0401B/NAKUSysOkArbtSNI07Ar/).

## What must be calculated

For each sector:

`necessary hours = physical output × person-hours per unit of output`

Then add:

- repair and replacement of fixed capital;
- inventory management and logistics;
- training and worker replacement;
- sick leave, vacation, and occupational transitions;
- export labour needed to import missing resources.

The final share is:

`population share = all necessary hours / available population hours`

At least three working-time regimes should be calculated: 40, 30, and 20 hours per week. This gives both the required worker share and a possible average working week.

## Sectors in the first calculation

1. Food and agriculture.
2. Electricity, heat, and fuel.
3. Water, sewage, and waste.
4. Housing, construction, and capital repair.
5. Medicine, care, and pharmaceuticals.
6. Transport, communications, and logistics.
7. Mining, metallurgy, chemicals, and equipment manufacturing.
8. Repair, spare parts, and infrastructure maintenance.
9. Education and specialist training.
10. Police, fire services, army, and emergency services.
11. Audit, IT, coordination, and foreign trade.
12. Worker reserve for failures and emergencies.

## Important boundaries

Current employment must not be treated as necessary by default. It includes luxury production, financial operations, advertising, excess administration, and export goods. But counting only direct workers is also wrong: steel production includes energy, repair, transport, equipment, and training.

Sweden is not assumed to be fully self-sufficient. For each scarce resource, specify whether it is:

- produced domestically;
- imported through export labour;
- replaced by a lower standard or another technology.

## First verifiable result

The first table should look like this:

| Sector | Required physical output | Hours per unit | Total hours | Bottleneck |
|---|---:|---:|---:|---|
| Food | TBD | TBD | TBD | land/seasonality |
| Energy | TBD | TBD | TBD | equipment/grid |
| Medicine and care | TBD | TBD | TBD | people |
| Repair | TBD | TBD | TBD | local availability |
| Industry | TBD | TBD | TBD | steel/machine tools |
| Exports for imports | TBD | TBD | TBD | external demand |

It is not yet honest to state a final percentage: official data give the total labour volume, but do not automatically provide a normative basic basket or the labour intensity of its required output. The next step is to choose the basic consumption level and fill in physical quantities for the first four sectors.
