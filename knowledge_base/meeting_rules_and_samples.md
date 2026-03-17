# Sample Meeting Decisions and JIRA Rules

## Examples of Past Meeting Decisions

### Deployment & Release
- Production deployment decisions are generally implemented in the next sprint.
- Hotfix decisions are implemented within 24 hours; the DevOps team must be notified.
- Maintenance windows are announced in advance; the typical window is between 02:00-06:00.
- QA approval is mandatory prior to any release.

### Performance & Technical Debt
- Performance issues are assigned to the relevant domain team (Backend/Mobile).
- Mobile application performance issues are specifically assigned to the Mobile team.
- Technical debt resolutions are planned and scheduled for the next sprint.

### Documentation
- Documentation deficiencies must be completed by the relevant team (Backend/Frontend/Mobile) within 2 weeks.
- If API documentation is missing, the strict deadline is set to 2 weeks.
- Model or data pipeline documentation tasks are assigned to the Data/AI team.

### Onboarding & HR
- Onboarding and HR-related tasks require direct coordination with the HR department.
- Onboarding documents for new interns/employees are prepared by the HR team.

### Data & AI
- Model performance anomalies are assigned to the Data/AI team.
- Data pipeline errors are assigned to the Data team and must be resolved within 1 week.
- AI model updates are rigorously tested in the staging environment before being deployed to production.

## JIRA Task Formatting Rules
- **Title:** Must use a team or domain prefix (e.g., [Backend], [Frontend], [Mobile], [Data], [AI], [DevOps], [HR]).
- **Description:** Clearly state what needs to be done, who is responsible, and the deadline (if applicable).
- **Tag Suggestions:** team-backend, team-frontend, team-mobile, team-data, team-ai, sprint-XX, documentation, performance, onboarding, hotfix, technical-debt, ml-model, data-pipeline.

## Priority Rules
- If a deadline is explicitly stated → **Priority: High**
- If the terms "urgent", "critical", or "today" are used → **Priority: High**
- If there is a direct production or customer impact → **Priority: High**
- If the task is planned for the upcoming sprint → **Priority: Medium**
- If the terms "research", "investigate", or "evaluate" are used → **Priority: Low**
- If the task is related to technical debt or general improvements → **Priority: Low**

## Decision → Task Examples
- **"Mobile app is slow"** → [Mobile] Application performance optimization | Priority: High | Tags: team-mobile, performance
- **"API v2 documentation is missing, will be completed in 2 weeks"** → [Backend] Complete API v2 documentation | Priority: High | Tags: team-backend, documentation
- **"Recommendation model will be tested in staging"** → [AI] Complete recommendation model staging test | Priority: Medium | Tags: team-ai, ml-model
- **"There is a delay in the data pipeline, needs investigation"** → [Data] Investigate data pipeline delay cause | Priority: Low | Tags: team-data, data-pipeline