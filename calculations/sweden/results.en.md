# Results

The final calculation is not filled in yet: the basic basket and task-level labour standards are not fixed. The first scenario result is in [results-v0.en.md](results-v0.en.md); it uses assumption ranges and does not replace the detailed model.

```text
total_required_hours = sum(total_labor_hours by sector)
required_FTE = total_required_hours / hours_per_FTE_per_year
share_of_population = required_FTE / population
share_of_workers = required_FTE / working_age_population
average_weekly_hours = total_required_hours / employed_or_working_population / 52
```

Domestic production, imports, and export labour must be shown separately. The current 5.263 million employed people are a calibration reference, not the answer.
