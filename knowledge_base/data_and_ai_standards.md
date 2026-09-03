# Data & AI Standards

## Ownership

- Model performance anomalies (accuracy drop, drift, unexpected outputs) are assigned to the Data/AI team, not Backend, even when the model is served through a backend API.
- Data pipeline errors (failed ETL jobs, corrupted data, missed schedules) are assigned to the Data team and must be resolved within 1 week — this is a firm SLA because downstream reports and models depend on it.

## Deployment gate

- AI model updates are rigorously tested in the staging environment before being deployed to production — this cannot be skipped even for a "small" model tweak.
- A model update task is not considered done until it has a documented staging evaluation result attached.

## Priority

- Data pipeline errors are `Priority: High` by default because of the 1-week SLA and downstream dependencies.
- Model performance anomalies are `Priority: Medium` unless they are actively causing incorrect production output, in which case they become `Priority: High`.
- New model research/exploration work is `Priority: Low`.
