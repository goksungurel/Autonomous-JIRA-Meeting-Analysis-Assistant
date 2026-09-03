# Priority Assignment Rules

Assign exactly one priority to every JIRA task: High, Medium, or Low. Evaluate the rules below in order — the first one that matches wins.

## Priority: High

- A concrete deadline was explicitly stated in the meeting.
- The words "urgent", "critical", "blocker", or "today" were used to describe the item.
- There is a direct, currently-live production or paying-customer impact.
- The item is a security issue of any kind.
- The item is a hotfix (see deployment rules — hotfixes are always High).

## Priority: Medium

- The task is planned for the upcoming sprint but has no hard deadline.
- The task affects an internal tool or an environment that is not production.
- The task was raised as "should do soon" without urgency language.

## Priority: Low

- The words "research", "investigate", "evaluate", or "explore" were used — anything exploratory defaults to Low unless another High rule also applies.
- The task is technical debt or a general code-quality improvement with no reported user impact.
- The task is a documentation or onboarding item with no stated deadline.

## Conflicts

If more than one rule matches, always take the higher priority. Example: a "critical" bug that is also framed as "investigate the root cause" is still High, not Low — urgency language always overrides exploratory language.
