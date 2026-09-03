# Deployment & Release Standards

## Regular releases

- Production deployment decisions made in a meeting are implemented in the next sprint by default, not immediately.
- Every release requires QA approval before it goes out — no exceptions, regardless of how small the change is.
- Maintenance windows are announced at least 24 hours in advance; the standard window is 02:00–06:00 local time.
- Release notes must list every JIRA task included in the release.

## Hotfixes

- A hotfix is any production fix that cannot wait for the next regular release.
- Hotfixes are implemented within 24 hours of the decision.
- The DevOps team must be notified immediately when a hotfix is decided, even before the JIRA task is created.
- Hotfixes always get `Priority: High` and the `hotfix` tag.
- A hotfix still requires a (fast-tracked) QA sign-off before deployment, never a full skip of QA.

## Rollbacks

- Any deployment that causes a production incident is rolled back first, root-caused second.
- Rollback decisions do not require the same approval chain as forward deployments — the on-call DevOps engineer can decide alone.

## Ownership

- Deployment and release tasks are owned by the DevOps team unless the meeting explicitly assigns them elsewhere.
