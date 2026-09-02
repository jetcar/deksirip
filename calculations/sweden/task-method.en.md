# Method for calculating the human minimum

## 1. Result first, occupation second

Ask what result is necessary, whether organization can remove the task, whether an automated system can deliver it reliably, and where human judgement, physical intervention, or responsibility remains.

## 2. Task classes

- **A — disappears:** the result is unnecessary or organization can remove the task;
- **B — automated:** the result is necessary, but a mature system can deliver it without a permanent human;
- **C — human exceptions:** the normal flow is automated, but people handle emergencies and unusual cases;
- **D — permanently human:** care, complex judgement, unpredictable physical work, or personal responsibility.

S3 counts hours for classes C and D, plus a control share of class B work.

## 3. What cannot be removed automatically

Automating checkout does not remove delivery, error control, returns, or accessibility. Automating cleaning does not remove sanitation, machine maintenance, or unusual contamination. A row is removed only after the complete process is checked.

## 4. Formula

```text
hours_i = required_output_i × human_hours_per_unit_i × (1 - reliable_automation_i)
          + exception_hours_i
```

Then add training, leave, sickness, emergency reserves, and intermediate suppliers' labour. Do not count the same labour twice: use either an input-output chain or a manual expansion.

## 5. Two limits

- **S3a:** remove only tasks for which automation already exists and can be scaled in Sweden;
- **S3b:** additionally remove tasks with technically plausible but not yet widespread automation.

S3b is a technological limit under a stated reliability level, not a near-term forecast.
