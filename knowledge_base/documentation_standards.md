# Documentation Standards

## Ownership and deadlines

- Documentation deficiencies are completed by the team that owns the underlying system — Backend, Frontend, or Mobile — within 2 weeks of being raised.
- If API documentation specifically is missing or outdated, the deadline is a strict 2 weeks; this is treated as a firm commitment, not a suggestion.
- Model or data pipeline documentation is assigned to the Data/AI team, not Backend, even if the pipeline runs on backend infrastructure.

## What counts as a documentation task

- Missing README sections, outdated setup instructions, undocumented API endpoints, and missing runbooks all count as documentation tasks.
- A documentation task should never be merged into a feature task — even when they're related, track them separately so documentation debt is visible on its own.

## Priority

- Documentation tasks default to `Priority: Low` unless the missing documentation is actively blocking another team (e.g., a partner team cannot integrate without it), in which case it becomes `Priority: Medium`.
