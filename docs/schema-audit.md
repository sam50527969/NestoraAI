# Database schema audit

The canonical SQLAlchemy metadata registry contains these 16 application tables:

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

## Repaired migration chain

The Alembic chain now reproduces the canonical schema from an empty database:

1. `d22c6b17208a` creates the historical base `leads` table.
2. `c5d8d829c5b8` adds the six nullable AI-memory fields.
3. `687dc4717df8` creates `marketing_plans`.
4. `522d2ff063fe` creates `missions`.
5. `f3fac4700001` adds the five nullable opportunity fields and creates the
   remaining 13 canonical tables.

Application startup continues to call `metadata.create_all()`. Migrations
therefore validate and preserve compatible tables that startup may already have
created rather than attempting to recreate them.

## Existing-database safety

Every revision preflights the objects relevant to its recorded predecessor
before issuing schema changes. Compatible existing objects are preserved. The
chain creates only missing tables and adds only the approved nullable lead
columns. It never automatically stamps an existing database.

Migration stops without changing application data when it encounters:

- an unversioned database that already contains application tables;
- a revision stamp whose required predecessor tables are missing;
- incompatible column types or nullability;
- incompatible primary keys or required uniqueness.

The convergence revision validates every existing canonical table before its
first schema change. Its downgrade is explicitly unsupported because removing
the completed schema could destroy application data. The repaired historical
revisions are also non-destructive on downgrade.

An existing, unversioned database requires a separately reviewed, manual
adoption process. Operators must never infer or apply a revision stamp merely
because tables exist.

## Migration testing

Migration tests use unique SQLite database files under pytest temporary
directories and explicitly set `DATABASE_URL` for every Alembic subprocess.
They never target the default `nestora.db` or another persistent database.

The tests cover:

- a fresh upgrade through the complete chain;
- upgrades from every historical revision;
- the exact 16-table canonical inventory;
- column, primary-key, type, and uniqueness expectations;
- compatible schemas previously completed by `metadata.create_all()`;
- preservation of existing lead, user, and business data;
- rejection of unversioned, contradictory, and incompatible schemas; and
- preservation of the startup `metadata.create_all()` behavior.

SQLite is the only migration-test dialect in this change. SQLite has limited
`ALTER TABLE` support, non-transactional DDL under Alembic, permissive string
lengths, integer-backed booleans, and timestamp behavior that differs from
PostgreSQL. To avoid unsafe table rebuilds, incompatible existing definitions
are rejected rather than coerced. PostgreSQL compatibility remains unverified
and requires separate approval and infrastructure.
