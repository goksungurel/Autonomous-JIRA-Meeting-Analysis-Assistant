# JIRA Task Formatting Rules

These are the mandatory formatting rules for every JIRA task created from a meeting. Apply them to every action item regardless of which team or domain it belongs to.

## Title

- Must start with a team or domain prefix in square brackets: `[Backend]`, `[Frontend]`, `[Mobile]`, `[Data]`, `[AI]`, `[DevOps]`, `[HR]`, `[QA]`.
- Keep the title under 80 characters.
- Use an action verb (Fix, Implement, Investigate, Complete, Optimize, Migrate) as the first word after the prefix.
- Do not restate the whole meeting sentence — summarize the decision, not the discussion.

## Description

- Clearly state what needs to be done.
- Name who is responsible if the meeting specified an owner or team.
- Include the deadline if one was mentioned, in `YYYY-MM-DD` format when a concrete date is known, otherwise as a relative deadline ("within 2 weeks", "next sprint").
- If the task originated from a bug report, include reproduction context if it was mentioned.

## Tag suggestions

Pick tags from this list based on the task's domain and nature — do not invent new tags:

`team-backend`, `team-frontend`, `team-mobile`, `team-data`, `team-ai`, `team-devops`, `team-hr`, `team-qa`, `sprint-current`, `sprint-next`, `documentation`, `performance`, `onboarding`, `hotfix`, `technical-debt`, `ml-model`, `data-pipeline`, `security`, `release`.

## Issue type

- Use `Bug` only if the meeting described broken/incorrect existing behavior.
- Use `Task` for new work, chores, and documentation.
- Use `Story` only if the meeting explicitly framed it as a new user-facing feature.
