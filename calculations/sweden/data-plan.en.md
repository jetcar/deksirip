# Sweden calculation data plan

## Principle

First measure actual output and actual hours, then construct normative scenarios. Do not simply add “useful industries”: one industry may produce basic goods, exports, and non-essential consumption at the same time.

For the human-minimum scenario, the unit of analysis is a **task**, not an occupation. An occupation is removed only after it has been decomposed into tasks and the reliably automatable tasks have been identified.

## Sector classification

| Group | Included | Calculation |
|---|---|---|
| Basic needs | food, energy, water, housing, medicine, transport, communications | physical standard × labour intensity |
| Maintenance | buildings, networks, equipment, roads, and transport | replacement volume × labour intensity |
| Supply chain | steel, chemicals, machine tools, spare parts, mining | intermediate inputs of basic sectors |
| Public functions | education, care, fire services, police, audit | access standard × labour intensity |
| Import loop | export goods and services paying for missing resources | required imports − domestic production |
| Non-essential | luxury, excess advertising, some finance and entertainment | excluded from S1 and S3; shown separately in S0 |

## Human-necessity filter

For every task ask:

1. Is the result necessary for the basic standard?
2. Can organization remove the task without automation?
3. Is there a mature technology that performs it reliably enough?
4. Is a person needed for care, responsibility, exceptions, or physical intervention?

S3 includes only necessary tasks for which organizational simplification is insufficient and no reliable replacement exists.

## Data sources and filling order

Use SCB labour-force and national-account tables for hours and employment; SCB input-output tables for output and intermediate inputs; Jordbruksverket for food; the Swedish Energy Agency for energy; SCB for housing and construction; and SCB/Socialstyrelsen for medicine and care.

1. Define S1: calories and protein, square metres, temperature, transport trips, and access to care.
2. Obtain physical S1 output for each group.
3. Find labour intensity per unit and include all intermediate links.
4. Add annual capital replacement and reserves.
5. Check external balance and imported materials and equipment.
6. Recalculate FTE, population share, and average working week.
7. Mark for every task whether it disappears in S3a, S3b, or neither.

## No false precision

If a sector has no physical standard and labour intensity, leave `TBD` in `model.csv`. Current employment is a control value, not the necessary minimum.
