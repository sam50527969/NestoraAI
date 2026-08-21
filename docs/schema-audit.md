# Database schema audit

The canonical SQLAlchemy metadata registry contains these 16 tables:

1. `agent_tasks`
2. `businesses`
3. `ceo_approvals`
4. `clinic_leads`
5. `collaboration_contributions`
6. `collaboration_sessions`
7. `executive_memory`
8. `executive_messages`
9. `follow_up_activities`
10. `leads`
11. `marketing_plans`
12. `mission_events`
13. `missions`
14. `outreach_activities`
15. `pipeline_activities`
16. `users`

## Existing migration-chain gaps

The existing Alembic chain has four revisions. It begins by creating `leads`,
then adds AI-memory fields, marketing-plan fields, and the `missions` table.
It does not fully reproduce the canonical metadata from an empty database:

- Most canonical tables have no create-table migration.
- The chain does not create all tables referenced by the current mapped models.
- Runtime `create_all` therefore still fills schema gaps during application startup.

This audit documents the existing state only. No revision or mapped-model design
is changed as part of the database configuration and metadata registry work.
