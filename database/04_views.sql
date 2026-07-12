-- =============================================================
-- CalcSync Database — Views
-- =============================================================
-- Run after schema.sql (and after seed.sql if you want the
-- views to return data immediately). Views are read-only and
-- have no side effects.
-- =============================================================

USE `CalcSync`;

-- -------------------------------------------------------------
-- VIEW: view_event_details
-- Denormalized event listing with human-readable type, status,
-- visibility, location and creator name.
-- -------------------------------------------------------------
DROP VIEW IF EXISTS `view_event_details`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER
VIEW `view_event_details` AS
SELECT
    e.event_id,
    e.title,
    e.description,
    e.start_time,
    e.end_time,
    u.name AS created_by,
    et.type_name AS event_type,
    es.status_name AS event_status,
    ev.visibility_name AS visibility,
    el.location_name AS location
FROM events e
JOIN users u ON e.created_by = u.user_id
LEFT JOIN event_types et ON e.type_id = et.type_id
LEFT JOIN event_status es ON e.status_id = es.status_id
LEFT JOIN event_visibility ev ON e.visibility_id = ev.visibility_id
LEFT JOIN event_locations el ON e.location_id = el.location_id;

-- -------------------------------------------------------------
-- VIEW: view_event_participant_count
-- Number of participants attached to each event.
-- -------------------------------------------------------------
DROP VIEW IF EXISTS `view_event_participant_count`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER
VIEW `view_event_participant_count` AS
SELECT
    e.event_id,
    e.title,
    u.name AS organizer,
    COUNT(ep.user_id) AS total_participants
FROM events e
JOIN users u ON e.created_by = u.user_id
LEFT JOIN event_participants ep ON e.event_id = ep.event_id
GROUP BY e.event_id, e.title, u.name;

-- -------------------------------------------------------------
-- VIEW: view_upcoming_events
-- Events whose start_time is in the future.
-- -------------------------------------------------------------
DROP VIEW IF EXISTS `view_upcoming_events`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER
VIEW `view_upcoming_events` AS
SELECT
    e.title,
    e.start_time,
    u.name
FROM events e
JOIN users u ON e.created_by = u.user_id
WHERE e.start_time > NOW();
