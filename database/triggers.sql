-- =============================================================
-- CalcSync Database — Triggers
-- =============================================================
-- Run after schema.sql (triggers reference `events`,
-- `activity_logs`, `notifications`, `audit_trail` and
-- `event_participants`, `event_invitations`, which must already
-- exist).
--
-- IMPORTANT: if you load seed.sql AFTER this file, the triggers
-- below will fire on every seeded INSERT into `events` and
-- `invitation_responses`. The original dump's seed data already
-- contains the rows these triggers would generate (see the notes
-- in seed.sql), so loading triggers.sql before seed.sql will
-- produce extra, duplicate rows in `activity_logs` and
-- `notifications`. See database_design.md for recommended
-- load order / workarounds.
-- =============================================================

USE `CalcSync`;

-- -------------------------------------------------------------
-- TRIGGER: before_event_insert  (BEFORE INSERT ON events)
-- Blocks inserting an event that overlaps another event already
-- owned by the same user.
-- -------------------------------------------------------------
DROP TRIGGER IF EXISTS `before_event_insert`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` TRIGGER `before_event_insert`
BEFORE INSERT ON `events`
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM events
        WHERE created_by = NEW.created_by
        AND (NEW.start_time < end_time AND NEW.end_time > start_time)
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Event time conflict detected';
    END IF;
END ;;
DELIMITER ;

-- -------------------------------------------------------------
-- TRIGGER: before_event_time_check  (BEFORE INSERT ON events)
-- Rejects events where end_time is not strictly after start_time.
-- -------------------------------------------------------------
DROP TRIGGER IF EXISTS `before_event_time_check`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` TRIGGER `before_event_time_check`
BEFORE INSERT ON `events`
FOR EACH ROW
BEGIN
    IF NEW.end_time <= NEW.start_time THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'End time must be after start time';
    END IF;
END ;;
DELIMITER ;

-- -------------------------------------------------------------
-- TRIGGER: after_event_insert_log  (AFTER INSERT ON events)
-- Records event creation in the activity log.
-- -------------------------------------------------------------
DROP TRIGGER IF EXISTS `after_event_insert_log`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` TRIGGER `after_event_insert_log`
AFTER INSERT ON `events`
FOR EACH ROW
BEGIN
    INSERT INTO activity_logs(user_id, action)
    VALUES (NEW.created_by, CONCAT('Created event: ', NEW.title));
END ;;
DELIMITER ;

-- -------------------------------------------------------------
-- TRIGGER: after_event_insert  (AFTER INSERT ON events)
-- Sends an in-app notification to the event creator.
-- -------------------------------------------------------------
DROP TRIGGER IF EXISTS `after_event_insert`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` TRIGGER `after_event_insert`
AFTER INSERT ON `events`
FOR EACH ROW
BEGIN
    INSERT INTO notifications (user_id, event_id, message, type_id)
    VALUES (NEW.created_by, NEW.event_id, 'New event created', 2);
END ;;
DELIMITER ;

-- -------------------------------------------------------------
-- TRIGGER: before_event_delete_audit  (BEFORE DELETE ON events)
-- Writes a snapshot of the deleted event to audit_trail.
-- -------------------------------------------------------------
DROP TRIGGER IF EXISTS `before_event_delete_audit`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` TRIGGER `before_event_delete_audit`
BEFORE DELETE ON `events`
FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (table_name, operation, changed_data, changed_at)
    VALUES (
        'events',
        'DELETE',
        CONCAT('Deleted: ', OLD.title,
               ' | Start: ', OLD.start_time,
               ' | End: ', OLD.end_time,
               ' | User: ', OLD.created_by),
        NOW()
    );
END ;;
DELIMITER ;

-- -------------------------------------------------------------
-- TRIGGER: after_invitation_response  (AFTER INSERT ON invitation_responses)
-- Promotes an invitation response into event_participants once a
-- receiver responds.
-- -------------------------------------------------------------
DROP TRIGGER IF EXISTS `after_invitation_response`;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` TRIGGER `after_invitation_response`
AFTER INSERT ON `invitation_responses`
FOR EACH ROW
BEGIN
    INSERT IGNORE INTO event_participants(event_id, user_id, status_id)
    SELECT event_id, receiver_id, NEW.status_id
    FROM event_invitations
    WHERE invitation_id = NEW.invitation_id;
END ;;
DELIMITER ;
