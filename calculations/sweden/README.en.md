# Sweden baseline calculations

Working folder for estimating the population share and person-hours required for a basic standard of living in Sweden, including a scenario for the minimum human labour remaining after automation.

The source baseline is described in [../../critique/28-sweden-baseline.en.md](../../critique/28-sweden-baseline.en.md).

## Files

- `inputs.csv` — source quantities and assumptions;
- `model.csv` — sector model;
- `assumptions.md` — current Sweden baseline and two future normative scenarios;
- `data-plan.md` — sector classification and data-filling procedure;
- `tasks.csv` — decomposition of the first sectors into necessary tasks;
- `task-method.md` — rule for deciding whether a task remains human;
- `scenario-s3-v0.csv` — first post-automation FTE range;
- `results-v0.md` — results and limitations of the first estimate;
- `productivity-scenarios.md` — how reducing the working week differs from reducing necessary labour itself;
- `work-organization.md` — self-regulation of schedules and the difference between calendar and effective hours;
- `results.md` — interpretation and limitations.

The latest result is in `results-v0.md` and is labelled S3-v1 there: care work has been separated from clinical medicine and education has been digitized.

In scenario S3, tasks must be counted rather than job titles: removing cashiers does not remove restocking, returns, and exception handling; removing cleaners does not remove sanitation.

## Units

- population — people;
- output — physical units per year;
- labour — person-hours per year;
- FTE — full-time equivalent;
- share — percentage of the total population or labour force, with the denominator stated.

## Status

The files below are a framework: first define the basic consumption basket, then fill in physical output and labour intensity by sector.
