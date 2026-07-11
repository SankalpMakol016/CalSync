# CalcSync — Database Design

## Overview

CalcSync is a relational calendar/event-scheduling system originally built as a
college DBMS project and now organized as a standalone, open-source-ready
database module. It models users, roles, events (with type/status/visibility/
location), invitations & RSVPs, recurrence rules, reminders, notifications,
and a set of audit/logging tables for activity tracking and conflict
detection.

- **Engine:** InnoDB
- **Character set:** `utf8mb4` / `utf8mb4_0900_ai_ci`
- **Database name:** `CalcSync`

## Tables

**30 tables**, grouped by concern:

| Group | Tables |
|---|---|
| Identity & access | `users`, `roles`, `user_roles`, `user_profiles`, `user_preferences` |
| Core scheduling | `events`, `event_types`, `event_status`, `event_visibility`, `event_locations` |
| Tagging | `event_tags`, `event_tag_map` |
| Collaboration | `event_participants`, `participant_status`, `event_invitations`, `invitation_responses` |
| Recurrence | `recurrence_types`, `recurrence_rules`, `recurrence_days`, `event_recurrence_map` |
| Notifications & reminders | `notification_types`, `notifications`, `notification_logs`, `reminders` |
| Availability | `user_availability`, `availability_slots` |
| Auditing & diagnostics | `activity_logs`, `audit_trail`, `conflict_logs`, `login_sessions` |

## Normalization Level

The schema is designed to **Third Normal Form (3NF)**:

- Every non-key attribute depends on the whole primary key and nothing but
  the key (e.g. event metadata is not duplicated — `event_types`,
  `event_status`, `event_visibility`, and `event_locations` are all broken
  out into their own lookup tables rather than stored as free text on
  `events`).
- Many-to-many relationships are resolved through explicit junction tables
  (`user_roles`, `event_tag_map`, `event_participants`) rather than
  repeating groups.
- Transitive dependencies are avoided — e.g. participant/invitation status
  is centralized in `participant_status` and referenced by both
  `event_participants` and `invitation_responses`, instead of being
  redefined per table.

A small, intentional exception: `audit_trail` has no foreign keys, so
historical records remain readable even after the rows they describe are
deleted. This is a standard trade-off for audit/log tables and does not
affect normalization of the operational data.

## Relationship Summary

- `users` is the anchor entity: it fans out to profiles, preferences,
  availability, sessions, roles, and everything the user creates or is
  involved in.
- `events` is the central entity: it references `users` (creator),
  `event_types`, `event_status`, `event_visibility`, and `event_locations`,
  and is in turn referenced by participants, invitations, tags, reminders,
  notifications, recurrence mapping, and conflict logs.
- `event_invitations` → `invitation_responses` → (trigger) →
  `event_participants` models the RSVP lifecycle: an invitation is sent,
  a response is recorded, and an accepted/declined response is promoted
  into the participants table automatically.
- `recurrence_rules` → `recurrence_days` and `event_recurrence_map` model
  recurring events (e.g. "every Monday and Wednesday until June 1st").
- `user_availability` → `availability_slots` models a user's free/busy
  windows per day of week.

See `CalcSync_er.svg` for the full entity-relationship diagram.

## Stored Procedures & Functions

Defined in `procedures.sql`:

| Name | Type | Purpose |
|---|---|---|
| `get_event_count(uid)` | Function | Total events created by a user |
| `get_event_duration(eid)` | Function | Duration of an event, in minutes |
| `get_upcoming_count(uid)` | Function | Count of a user's future events |
| `check_availability(p_user, p_start, p_end)` | Procedure | Finds a user's events overlapping a given window |
| `create_event(t, s, e, u)` | Procedure | Inserts a new event |
| `get_event_stats()` | Procedure | Per-user totals: total / upcoming / past events, earliest/latest |
| `get_top_users()` | Procedure | Users ranked by number of events created |
| `get_user_events(p_user)` | Procedure | A user's events, ordered by start time |

## Triggers

Defined in `triggers.sql`:

| Name | Fires On | Purpose |
|---|---|---|
| `before_event_insert` | `BEFORE INSERT` on `events` | Rejects an event that overlaps another event by the same creator |
| `before_event_time_check` | `BEFORE INSERT` on `events` | Rejects an event whose `end_time` isn't after its `start_time` |
| `after_event_insert_log` | `AFTER INSERT` on `events` | Writes a "Created event: …" row to `activity_logs` |
| `after_event_insert` | `AFTER INSERT` on `events` | Sends an in-app notification to the event creator |
| `before_event_delete_audit` | `BEFORE DELETE` on `events` | Snapshots the deleted event into `audit_trail` |
| `after_invitation_response` | `AFTER INSERT` on `invitation_responses` | Promotes a response into `event_participants` |

## Views

Defined in `views.sql`:

- **`view_event_details`** — denormalized event listing (creator name, type,
  status, visibility, location) for read-heavy display screens.
- **`view_event_participant_count`** — participant count per event.
- **`view_upcoming_events`** — events whose `start_time` is in the future.

## Design Decisions

- **Lookup tables over enums/strings.** Types, statuses, visibility levels,
  tags, roles, and notification channels are all normalized into their own
  tables instead of being hardcoded as `ENUM` or free-text columns. This
  keeps the vocabulary extensible without a schema migration (e.g. adding a
  new event type is an `INSERT`, not an `ALTER TABLE`).
- **Business rules enforced at the database layer.** Overlap detection and
  start/end time validity are enforced by triggers on `events`, so the
  invariant holds regardless of which application or client performs the
  insert.
- **Automatic side effects via triggers.** Event creation automatically
  produces an activity-log entry and a notification; invitation responses
  automatically produce a participant record. This keeps derived state
  consistent without relying on application code to remember to do it.
- **Separate logging vs. auditing tables.** `activity_logs` is a
  human-readable action feed; `audit_trail` is a structural change record
  (currently populated only for event deletes); `conflict_logs` and
  `notification_logs` are narrowly scoped to their own subsystems. Keeping
  these separate avoids a single overloaded "logs" table.

## How to Initialize the Database

Run the files in this order:

```bash
mysql -u root -p < schema.sql
mysql -u root -p < procedures.sql
mysql -u root -p < triggers.sql
mysql -u root -p < views.sql
mysql -u root -p < seed.sql   # optional — demo/sample data
```

Or, from within a MySQL client already connected to the server:

```sql
SOURCE schema.sql;
SOURCE procedures.sql;
SOURCE triggers.sql;
SOURCE views.sql;
SOURCE seed.sql;
```

> **Note on seed data + triggers:** `events` and `invitation_responses`
> both have `AFTER INSERT` triggers that write to `activity_logs`,
> `notifications`, and `event_participants`. The rows in `seed.sql` already
> include the log/notification rows that these triggers would generate, so
> loading `triggers.sql` before `seed.sql` (the order above) will produce
> some duplicate-looking rows in `activity_logs` and `notifications` —
> this is expected and explained further in the "Issues Found" section of
> the conversion summary. If you want a duplicate-free import, load
> `seed.sql` before `triggers.sql` instead.

## Requirements

- MySQL 8.0+ or MariaDB 10.6+ (uses `utf8mb4_0900_ai_ci`, a MySQL 8
  collation — see compatibility note in the conversion summary if you need
  MariaDB support).
