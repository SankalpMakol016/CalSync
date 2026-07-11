-- =============================================================
-- CalcSync Database — Stored Procedures & Functions
-- =============================================================
-- Run after schema.sql. All routines reference tables from
-- schema.sql only; none depend on seed data.
--
-- NOTE: the original dump also defined three stored FUNCTIONS
-- alongside the procedures. MySQL groups functions and
-- procedures together as "routines", so they are kept in this
-- single file rather than being split further. They are listed
-- first below.
-- =============================================================

USE `CalcSync`;

-- -------------------------------------------------------------
-- FUNCTION: get_event_count
-- Returns the total number of events created by a given user.
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS `get_event_count`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `get_event_count`(uid INT)
RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE c INT;
    SELECT COUNT(*) INTO c FROM events WHERE created_by = uid;
    RETURN c;
END ;;
DELIMITER ;

-- -------------------------------------------------------------
-- FUNCTION: get_event_duration
-- Returns the duration (in minutes) of a given event.
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS `get_event_duration`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `get_event_duration`(eid INT)
RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE d INT;
    SELECT TIMESTAMPDIFF(MINUTE, start_time, end_time)
    INTO d FROM events WHERE event_id = eid;
    RETURN d;
END ;;
DELIMITER ;

-- -------------------------------------------------------------
-- FUNCTION: get_upcoming_count
-- Returns the number of future events for a given user.
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS `get_upcoming_count`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `get_upcoming_count`(uid INT)
RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE c INT;
    SELECT COUNT(*) INTO c
    FROM events
    WHERE created_by = uid AND start_time > NOW();
    RETURN c;
END ;;
DELIMITER ;

-- -------------------------------------------------------------
-- PROCEDURE: check_availability
-- Returns any events for a user that overlap a given time range.
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS `check_availability`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `check_availability`(
    IN p_user INT,
    IN p_start DATETIME,
    IN p_end DATETIME
)
BEGIN
    SELECT * FROM events
    WHERE created_by = p_user
    AND (p_start < end_time AND p_end > start_time);
END ;;
DELIMITER ;

-- -------------------------------------------------------------
-- PROCEDURE: create_event
-- Inserts a new event for a user.
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS `create_event`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_event`(
    IN t VARCHAR(150),
    IN s DATETIME,
    IN e DATETIME,
    IN u INT
)
BEGIN
    INSERT INTO events(title, start_time, end_time, created_by) VALUES (t, s, e, u);
END ;;
DELIMITER ;

-- -------------------------------------------------------------
-- PROCEDURE: get_event_stats
-- Per-user summary of total / upcoming / past events.
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS `get_event_stats`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_event_stats`()
BEGIN
    SELECT
        u.name,
        COUNT(e.event_id) AS total_events,
        COUNT(CASE WHEN e.start_time > NOW() THEN 1 END) AS upcoming_events,
        COUNT(CASE WHEN e.start_time <= NOW() THEN 1 END) AS past_events,
        MIN(e.start_time) AS earliest_event,
        MAX(e.start_time) AS latest_event
    FROM users u
    LEFT JOIN events e ON u.user_id = e.created_by
    GROUP BY u.user_id, u.name
    ORDER BY total_events DESC;
END ;;
DELIMITER ;

-- -------------------------------------------------------------
-- PROCEDURE: get_top_users
-- Users ranked by number of events created (excludes zero).
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS `get_top_users`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_top_users`()
BEGIN
    SELECT user_name, total_events
    FROM (
        SELECT
            u.name AS user_name,
            COUNT(e.event_id) AS total_events
        FROM users u
        LEFT JOIN events e ON u.user_id = e.created_by
        GROUP BY u.user_id, u.name
    ) AS user_event_counts
    WHERE total_events > 0
    ORDER BY total_events DESC;
END ;;
DELIMITER ;

-- -------------------------------------------------------------
-- PROCEDURE: get_user_events
-- All events created by a given user, chronologically.
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS `get_user_events`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_user_events`(IN p_user INT)
BEGIN
    SELECT * FROM events
    WHERE created_by = p_user
    ORDER BY start_time;
END ;;
DELIMITER ;
