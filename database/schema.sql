-- =============================================================
-- CalcSync Database — Schema Definition
-- =============================================================
-- Contains: database creation, table structures, primary keys,
-- foreign keys, indexes and constraints only.
-- No data, no procedures, no triggers, no views (see other files).
-- =============================================================

CREATE DATABASE IF NOT EXISTS `CalcSync`
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE `CalcSync`;

-- -------------------------------------------------------------
-- Table: users
-- Core account table. All user-owned data hangs off this table.
-- -------------------------------------------------------------
CREATE TABLE `users` (
    `user_id`    INT NOT NULL AUTO_INCREMENT,
    `name`       VARCHAR(100) NOT NULL,
    `email`      VARCHAR(150) NOT NULL,
    `password`   VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`user_id`),
    UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: roles
-- Lookup table of available roles (admin, user, guest).
-- -------------------------------------------------------------
CREATE TABLE `roles` (
    `role_id`   INT NOT NULL AUTO_INCREMENT,
    `role_name` VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (`role_id`),
    UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: user_roles
-- Many-to-many join between users and roles.
-- -------------------------------------------------------------
CREATE TABLE `user_roles` (
    `user_id` INT NOT NULL,
    `role_id` INT NOT NULL,
    PRIMARY KEY (`user_id`, `role_id`),
    KEY `role_id` (`role_id`),
    CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
    CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: event_types
-- Lookup table of event categories (meeting, gym, exam, ...).
-- -------------------------------------------------------------
CREATE TABLE `event_types` (
    `type_id`   INT NOT NULL AUTO_INCREMENT,
    `type_name` VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (`type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: event_status
-- Lookup table of event lifecycle states.
-- -------------------------------------------------------------
CREATE TABLE `event_status` (
    `status_id`   INT NOT NULL AUTO_INCREMENT,
    `status_name` VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (`status_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: event_visibility
-- Lookup table of visibility levels (private, public, shared).
-- -------------------------------------------------------------
CREATE TABLE `event_visibility` (
    `visibility_id`   INT NOT NULL AUTO_INCREMENT,
    `visibility_name` VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (`visibility_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: event_locations
-- Lookup table of physical/virtual locations for events.
-- -------------------------------------------------------------
CREATE TABLE `event_locations` (
    `location_id`   INT NOT NULL AUTO_INCREMENT,
    `location_name` VARCHAR(100) DEFAULT NULL,
    `address`       TEXT,
    PRIMARY KEY (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: events
-- Central table of the schema — every calendar event.
-- -------------------------------------------------------------
CREATE TABLE `events` (
    `event_id`     INT NOT NULL AUTO_INCREMENT,
    `title`        VARCHAR(150) DEFAULT NULL,
    `description`  TEXT,
    `start_time`   DATETIME DEFAULT NULL,
    `end_time`     DATETIME DEFAULT NULL,
    `created_by`   INT DEFAULT NULL,
    `type_id`      INT DEFAULT NULL,
    `status_id`    INT DEFAULT NULL,
    `visibility_id` INT DEFAULT NULL,
    `location_id`  INT DEFAULT NULL,
    `created_at`   TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`event_id`),
    KEY `created_by` (`created_by`),
    KEY `type_id` (`type_id`),
    KEY `status_id` (`status_id`),
    KEY `visibility_id` (`visibility_id`),
    KEY `location_id` (`location_id`),
    CONSTRAINT `events_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
    CONSTRAINT `events_ibfk_2` FOREIGN KEY (`type_id`) REFERENCES `event_types` (`type_id`),
    CONSTRAINT `events_ibfk_3` FOREIGN KEY (`status_id`) REFERENCES `event_status` (`status_id`),
    CONSTRAINT `events_ibfk_4` FOREIGN KEY (`visibility_id`) REFERENCES `event_visibility` (`visibility_id`),
    CONSTRAINT `events_ibfk_5` FOREIGN KEY (`location_id`) REFERENCES `event_locations` (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: event_tags
-- Lookup table of free-form tags (gym, study, work, ...).
-- -------------------------------------------------------------
CREATE TABLE `event_tags` (
    `tag_id`   INT NOT NULL AUTO_INCREMENT,
    `tag_name` VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (`tag_id`),
    UNIQUE KEY `tag_name` (`tag_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: event_tag_map
-- Many-to-many join between events and tags.
-- -------------------------------------------------------------
CREATE TABLE `event_tag_map` (
    `event_id` INT NOT NULL,
    `tag_id`   INT NOT NULL,
    PRIMARY KEY (`event_id`, `tag_id`),
    KEY `tag_id` (`tag_id`),
    CONSTRAINT `event_tag_map_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`),
    CONSTRAINT `event_tag_map_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `event_tags` (`tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: participant_status
-- Lookup table of RSVP states (pending, accepted, rejected).
-- -------------------------------------------------------------
CREATE TABLE `participant_status` (
    `status_id`   INT NOT NULL AUTO_INCREMENT,
    `status_name` VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (`status_id`),
    UNIQUE KEY `status_name` (`status_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: event_participants
-- Many-to-many join between events and users, with RSVP status.
-- -------------------------------------------------------------
CREATE TABLE `event_participants` (
    `event_id`  INT NOT NULL,
    `user_id`   INT NOT NULL,
    `status_id` INT DEFAULT NULL,
    `added_at`  TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`event_id`, `user_id`),
    KEY `user_id` (`user_id`),
    KEY `status_id` (`status_id`),
    CONSTRAINT `event_participants_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`),
    CONSTRAINT `event_participants_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
    CONSTRAINT `event_participants_ibfk_3` FOREIGN KEY (`status_id`) REFERENCES `participant_status` (`status_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: event_invitations
-- Tracks invitations sent between users for a given event.
-- -------------------------------------------------------------
CREATE TABLE `event_invitations` (
    `invitation_id` INT NOT NULL AUTO_INCREMENT,
    `event_id`      INT DEFAULT NULL,
    `sender_id`     INT DEFAULT NULL,
    `receiver_id`   INT DEFAULT NULL,
    `sent_at`       TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`invitation_id`),
    KEY `event_id` (`event_id`),
    KEY `sender_id` (`sender_id`),
    KEY `receiver_id` (`receiver_id`),
    CONSTRAINT `event_invitations_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`),
    CONSTRAINT `event_invitations_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `users` (`user_id`),
    CONSTRAINT `event_invitations_ibfk_3` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: invitation_responses
-- Records a receiver's response to an event invitation.
-- -------------------------------------------------------------
CREATE TABLE `invitation_responses` (
    `response_id`   INT NOT NULL AUTO_INCREMENT,
    `invitation_id` INT DEFAULT NULL,
    `status_id`     INT DEFAULT NULL,
    `response_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`response_id`),
    KEY `invitation_id` (`invitation_id`),
    KEY `status_id` (`status_id`),
    CONSTRAINT `invitation_responses_ibfk_1` FOREIGN KEY (`invitation_id`) REFERENCES `event_invitations` (`invitation_id`),
    CONSTRAINT `invitation_responses_ibfk_2` FOREIGN KEY (`status_id`) REFERENCES `participant_status` (`status_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: recurrence_types
-- Lookup table of recurrence frequencies (daily, weekly, monthly).
-- -------------------------------------------------------------
CREATE TABLE `recurrence_types` (
    `recurrence_type_id` INT NOT NULL AUTO_INCREMENT,
    `type_name`           VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (`recurrence_type_id`),
    UNIQUE KEY `type_name` (`type_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: recurrence_rules
-- Defines a recurrence pattern (interval, start/end date).
-- -------------------------------------------------------------
CREATE TABLE `recurrence_rules` (
    `recurrence_id`      INT NOT NULL AUTO_INCREMENT,
    `recurrence_type_id` INT DEFAULT NULL,
    `interval_value`     INT DEFAULT '1',
    `start_date`         DATE DEFAULT NULL,
    `end_date`           DATE DEFAULT NULL,
    PRIMARY KEY (`recurrence_id`),
    KEY `recurrence_type_id` (`recurrence_type_id`),
    CONSTRAINT `recurrence_rules_ibfk_1` FOREIGN KEY (`recurrence_type_id`) REFERENCES `recurrence_types` (`recurrence_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: recurrence_days
-- Days of the week associated with a recurrence rule.
-- -------------------------------------------------------------
CREATE TABLE `recurrence_days` (
    `recurrence_day_id` INT NOT NULL AUTO_INCREMENT,
    `recurrence_id`      INT DEFAULT NULL,
    `day_of_week`        VARCHAR(10) DEFAULT NULL,
    PRIMARY KEY (`recurrence_day_id`),
    KEY `recurrence_id` (`recurrence_id`),
    CONSTRAINT `recurrence_days_ibfk_1` FOREIGN KEY (`recurrence_id`) REFERENCES `recurrence_rules` (`recurrence_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: event_recurrence_map
-- One-to-one link between an event and its recurrence rule.
-- -------------------------------------------------------------
CREATE TABLE `event_recurrence_map` (
    `event_id`      INT NOT NULL,
    `recurrence_id` INT DEFAULT NULL,
    PRIMARY KEY (`event_id`),
    KEY `recurrence_id` (`recurrence_id`),
    CONSTRAINT `event_recurrence_map_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`),
    CONSTRAINT `event_recurrence_map_ibfk_2` FOREIGN KEY (`recurrence_id`) REFERENCES `recurrence_rules` (`recurrence_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: notification_types
-- Lookup table of notification channels (email, in-app, sms).
-- -------------------------------------------------------------
CREATE TABLE `notification_types` (
    `type_id`   INT NOT NULL AUTO_INCREMENT,
    `type_name` VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (`type_id`),
    UNIQUE KEY `type_name` (`type_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: notifications
-- Notifications generated for users, optionally tied to an event.
-- -------------------------------------------------------------
CREATE TABLE `notifications` (
    `notification_id` INT NOT NULL AUTO_INCREMENT,
    `user_id`          INT DEFAULT NULL,
    `event_id`         INT DEFAULT NULL,
    `message`          TEXT,
    `type_id`          INT DEFAULT NULL,
    `created_at`       TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`notification_id`),
    KEY `user_id` (`user_id`),
    KEY `event_id` (`event_id`),
    KEY `type_id` (`type_id`),
    CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
    CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`),
    CONSTRAINT `notifications_ibfk_3` FOREIGN KEY (`type_id`) REFERENCES `notification_types` (`type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: notification_logs
-- Delivery log for each notification that was sent.
-- -------------------------------------------------------------
CREATE TABLE `notification_logs` (
    `log_id`          INT NOT NULL AUTO_INCREMENT,
    `notification_id` INT DEFAULT NULL,
    `sent_time`       TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    `status`          VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (`log_id`),
    KEY `notification_id` (`notification_id`),
    CONSTRAINT `notification_logs_ibfk_1` FOREIGN KEY (`notification_id`) REFERENCES `notifications` (`notification_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: reminders
-- Per-user, per-event reminder offsets (minutes before start).
-- -------------------------------------------------------------
CREATE TABLE `reminders` (
    `reminder_id`   INT NOT NULL AUTO_INCREMENT,
    `event_id`      INT DEFAULT NULL,
    `user_id`       INT DEFAULT NULL,
    `remind_before` INT DEFAULT NULL,
    `created_at`    TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`reminder_id`),
    KEY `event_id` (`event_id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `reminders_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`),
    CONSTRAINT `reminders_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: activity_logs
-- Free-text audit trail of user actions across the app.
-- -------------------------------------------------------------
CREATE TABLE `activity_logs` (
    `log_id`      INT NOT NULL AUTO_INCREMENT,
    `user_id`     INT DEFAULT NULL,
    `action`      VARCHAR(100) DEFAULT NULL,
    `action_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`log_id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `activity_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: audit_trail
-- Structural change log (INSERT/UPDATE/DELETE) populated by
-- triggers on tracked tables. Intentionally has no FKs so that
-- history survives even if referenced rows are removed.
-- -------------------------------------------------------------
CREATE TABLE `audit_trail` (
    `audit_id`     INT NOT NULL AUTO_INCREMENT,
    `table_name`   VARCHAR(100) DEFAULT NULL,
    `operation`    VARCHAR(20) DEFAULT NULL,
    `changed_data` TEXT,
    `changed_at`   TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`audit_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: conflict_logs
-- Records detected scheduling conflicts between two events.
-- -------------------------------------------------------------
CREATE TABLE `conflict_logs` (
    `conflict_id`          INT NOT NULL AUTO_INCREMENT,
    `user_id`              INT DEFAULT NULL,
    `event_id`             INT DEFAULT NULL,
    `conflicting_event_id` INT DEFAULT NULL,
    `detected_at`          TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`conflict_id`),
    KEY `user_id` (`user_id`),
    KEY `event_id` (`event_id`),
    KEY `conflicting_event_id` (`conflicting_event_id`),
    CONSTRAINT `conflict_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
    CONSTRAINT `conflict_logs_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`),
    CONSTRAINT `conflict_logs_ibfk_3` FOREIGN KEY (`conflicting_event_id`) REFERENCES `events` (`event_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: login_sessions
-- Tracks login/logout timestamps per user session.
-- -------------------------------------------------------------
CREATE TABLE `login_sessions` (
    `session_id`  INT NOT NULL AUTO_INCREMENT,
    `user_id`     INT DEFAULT NULL,
    `login_time`  TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    `logout_time` TIMESTAMP NULL DEFAULT NULL,
    PRIMARY KEY (`session_id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `login_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: user_availability
-- Per-user, per-day-of-week availability flag.
-- -------------------------------------------------------------
CREATE TABLE `user_availability` (
    `availability_id` INT NOT NULL AUTO_INCREMENT,
    `user_id`          INT DEFAULT NULL,
    `day_of_week`      VARCHAR(10) DEFAULT NULL,
    `is_available`     TINYINT(1) DEFAULT '1',
    PRIMARY KEY (`availability_id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `user_availability_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: availability_slots
-- Concrete time windows within an availability record.
-- -------------------------------------------------------------
CREATE TABLE `availability_slots` (
    `slot_id`         INT NOT NULL AUTO_INCREMENT,
    `availability_id` INT DEFAULT NULL,
    `start_time`      TIME DEFAULT NULL,
    `end_time`        TIME DEFAULT NULL,
    PRIMARY KEY (`slot_id`),
    KEY `availability_id` (`availability_id`),
    CONSTRAINT `availability_slots_ibfk_1` FOREIGN KEY (`availability_id`) REFERENCES `user_availability` (`availability_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: user_preferences
-- App-level display and reminder preferences per user.
-- -------------------------------------------------------------
CREATE TABLE `user_preferences` (
    `preference_id`    INT NOT NULL AUTO_INCREMENT,
    `user_id`          INT DEFAULT NULL,
    `theme`            VARCHAR(20) DEFAULT NULL,
    `default_reminder` INT DEFAULT NULL,
    `timezone`         VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (`preference_id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `user_preferences_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table: user_profiles
-- Extended profile information per user.
-- -------------------------------------------------------------
CREATE TABLE `user_profiles` (
    `profile_id` INT NOT NULL AUTO_INCREMENT,
    `user_id`    INT DEFAULT NULL,
    `phone`      VARCHAR(15) DEFAULT NULL,
    `timezone`   VARCHAR(50) DEFAULT NULL,
    `bio`        TEXT,
    PRIMARY KEY (`profile_id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `user_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
