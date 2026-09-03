# Performance & Technical Debt Standards

## Ownership by domain

- General performance issues are assigned to the relevant domain team — Backend for API/server-side slowness, Mobile for in-app performance.
- Mobile application performance issues (slow screens, jank, high battery/memory use) are always assigned to the Mobile team specifically, even if the root cause turns out to be a backend API.
- Database and query performance issues go to Backend, not Data, unless they involve the analytics/data warehouse stack.

## Technical debt

- Technical debt resolutions are planned work, not urgent work — they are scheduled for the next sprint by default, never the current one, unless a meeting explicitly escalates them.
- Technical debt tasks default to `Priority: Low` unless they are blocking another in-progress feature, in which case they inherit that feature's priority.
- Refactoring proposed "in passing" during a meeting (not the main topic) should still be captured as its own separate task, not folded into whatever feature was being discussed.

## Investigation vs. fix

- If a performance problem's cause is unknown, create an "Investigate" task first (Low priority unless there's active customer impact), not a fix task with a guessed solution.
- Once the cause is confirmed, a separate fix task is created and linked to the investigation task.
