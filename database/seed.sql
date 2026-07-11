-- =============================================================
-- CalcSync Database — Seed / Demo Data
-- =============================================================
-- Sample data for local development and demos. Statements are
-- ordered to satisfy foreign-key dependencies (same order as
-- schema.sql). Data values are unchanged from the original dump.
-- Run this after schema.sql, procedures.sql, triggers.sql and
-- views.sql have been applied.
-- =============================================================

USE `CalcSync`;

SET FOREIGN_KEY_CHECKS = 0;

-- users
INSERT INTO `users` VALUES
(1,'Sankalp','sankalp@gmail.com','pass123','2026-04-01 18:04:13'),
(2,'Rahul','rahul@gmail.com','pass123','2026-04-01 18:04:13'),
(3,'Amit','amit@gmail.com','pass123','2026-04-01 18:04:13'),
(4,'NoEvent1','no1@gmail.com','pass123','2026-04-01 18:10:14'),
(5,'NoEvent2','no2@gmail.com','pass123','2026-04-01 18:10:14');

-- roles
INSERT INTO `roles` VALUES (1,'admin'),(3,'guest'),(2,'user');

-- user_roles
INSERT INTO `user_roles` VALUES (1,1),(2,2),(3,3);

-- event_types
INSERT INTO `event_types` VALUES (1,'meeting'),(2,'gym'),(3,'exam');

-- event_status
INSERT INTO `event_status` VALUES (1,'scheduled'),(2,'completed'),(3,'cancelled');

-- event_visibility
INSERT INTO `event_visibility` VALUES (1,'private'),(2,'public'),(3,'shared');

-- event_locations
INSERT INTO `event_locations` VALUES (1,'Gym','Campus Gym'),(2,'Classroom','Block A'),(3,'Library','Campus');

-- events
-- NOTE: importing these rows will fire the `before_event_insert`,
-- `before_event_time_check`, `after_event_insert_log` and
-- `after_event_insert` triggers defined in triggers.sql.
INSERT INTO `events` VALUES
(1,'Gym Workout','Evening','2026-05-01 18:00:00','2026-05-01 19:00:00',1,2,1,1,1,'2026-04-01 18:04:13'),
(2,'Meeting','DBMS','2026-05-02 10:00:00','2026-05-02 11:00:00',2,1,1,2,2,'2026-04-01 18:04:13'),
(3,'Study','Exam','2026-05-03 09:00:00','2026-05-03 11:00:00',3,3,1,3,3,'2026-04-01 18:04:13'),
(4,'Short1',NULL,'2026-05-10 10:00:00','2026-05-10 10:30:00',1,NULL,NULL,NULL,NULL,'2026-04-01 18:11:13'),
(5,'Short2',NULL,'2026-05-10 11:00:00','2026-05-10 11:30:00',2,NULL,NULL,NULL,NULL,'2026-04-01 18:11:13'),
(6,'Long1',NULL,'2026-05-10 12:00:00','2026-05-10 14:00:00',1,NULL,NULL,NULL,NULL,'2026-04-01 18:11:13'),
(7,'Long2',NULL,'2026-05-10 15:00:00','2026-05-10 17:00:00',2,NULL,NULL,NULL,NULL,'2026-04-01 18:11:13'),
(8,'Extra1',NULL,'2026-05-11 10:00:00','2026-05-11 11:00:00',1,NULL,NULL,NULL,NULL,'2026-04-01 18:11:50'),
(9,'Extra2',NULL,'2026-05-11 12:00:00','2026-05-11 13:00:00',2,NULL,NULL,NULL,NULL,'2026-04-01 18:11:50');

-- event_tags
INSERT INTO `event_tags` VALUES (1,'gym'),(2,'study'),(3,'work');

-- event_tag_map
INSERT INTO `event_tag_map` VALUES (1,1),(2,2),(3,3);

-- participant_status
INSERT INTO `participant_status` VALUES (2,'accepted'),(1,'pending'),(3,'rejected');

-- event_participants
INSERT INTO `event_participants` VALUES
(1,2,2,'2026-04-01 18:04:13'),
(2,3,1,'2026-04-01 18:04:13'),
(3,1,2,'2026-04-01 18:04:13');

-- event_invitations
INSERT INTO `event_invitations` VALUES
(1,1,1,2,'2026-04-01 18:04:13'),
(2,2,2,3,'2026-04-01 18:04:13'),
(3,3,3,1,'2026-04-01 18:04:13');

-- invitation_responses
-- NOTE: importing these rows will fire the `after_invitation_response`
-- trigger defined in triggers.sql.
INSERT INTO `invitation_responses` VALUES
(1,1,2,'2026-04-01 18:04:13'),
(2,2,1,'2026-04-01 18:04:13'),
(3,3,2,'2026-04-01 18:04:13');

-- recurrence_types
INSERT INTO `recurrence_types` VALUES (1,'daily'),(3,'monthly'),(2,'weekly');

-- recurrence_rules
INSERT INTO `recurrence_rules` VALUES
(1,1,1,'2026-05-01','2026-06-01'),
(2,2,1,'2026-05-01','2026-06-01'),
(3,3,1,'2026-05-01','2026-06-01');

-- recurrence_days
INSERT INTO `recurrence_days` VALUES (1,1,'Monday'),(2,2,'Tuesday'),(3,3,'Wednesday');

-- event_recurrence_map
INSERT INTO `event_recurrence_map` VALUES (1,1),(2,2),(3,3);

-- notification_types
INSERT INTO `notification_types` VALUES (1,'email'),(2,'in-app'),(3,'sms');

-- notifications
INSERT INTO `notifications` VALUES
(1,1,1,'New event created',1,'2026-04-01 18:04:13'),
(2,2,2,'New event created',1,'2026-04-01 18:04:13'),
(3,3,3,'New event created',1,'2026-04-01 18:04:13'),
(4,1,1,'Reminder',1,'2026-04-01 18:06:24'),
(5,2,2,'Meeting Alert',2,'2026-04-01 18:06:24'),
(6,3,3,'Study Alert',3,'2026-04-01 18:06:24'),
(7,1,4,'New event created',1,'2026-04-01 18:11:13'),
(8,2,5,'New event created',1,'2026-04-01 18:11:13'),
(9,1,6,'New event created',1,'2026-04-01 18:11:13'),
(10,2,7,'New event created',1,'2026-04-01 18:11:13'),
(11,1,8,'New event created',1,'2026-04-01 18:11:50'),
(12,2,9,'New event created',1,'2026-04-01 18:11:50');

-- notification_logs
INSERT INTO `notification_logs` VALUES
(1,1,'2026-04-01 18:06:24','sent'),
(2,2,'2026-04-01 18:06:24','sent'),
(3,3,'2026-04-01 18:06:24','sent');

-- reminders
INSERT INTO `reminders` VALUES
(1,1,1,10,'2026-04-01 18:06:24'),
(2,2,2,15,'2026-04-01 18:06:24'),
(3,3,3,5,'2026-04-01 18:06:24');

-- activity_logs
-- NOTE: rows 1-6 are original seed data; rows 7-12 were also
-- produced as a side effect of the `after_event_insert_log`
-- trigger when events 4-9 above were first inserted, and are
-- preserved here exactly as they appeared in the source dump.
INSERT INTO `activity_logs` VALUES
(1,1,'Created event: Gym Workout','2026-04-01 18:04:13'),
(2,2,'Created event: Meeting','2026-04-01 18:04:13'),
(3,3,'Created event: Study','2026-04-01 18:04:13'),
(4,1,'Created event','2026-04-01 18:07:22'),
(5,2,'Joined event','2026-04-01 18:07:22'),
(6,3,'Updated profile','2026-04-01 18:07:22'),
(7,1,'Created event: Short1','2026-04-01 18:11:13'),
(8,2,'Created event: Short2','2026-04-01 18:11:13'),
(9,1,'Created event: Long1','2026-04-01 18:11:13'),
(10,2,'Created event: Long2','2026-04-01 18:11:13'),
(11,1,'Created event: Extra1','2026-04-01 18:11:50'),
(12,2,'Created event: Extra2','2026-04-01 18:11:50');

-- audit_trail
INSERT INTO `audit_trail` VALUES
(1,'events','INSERT','Gym added','2026-04-01 18:07:22'),
(2,'events','UPDATE','Changed','2026-04-01 18:07:22'),
(3,'events','DELETE','Removed','2026-04-01 18:07:22');

-- conflict_logs
INSERT INTO `conflict_logs` VALUES
(1,1,1,2,'2026-04-01 18:19:05'),
(2,2,2,3,'2026-04-01 18:19:05'),
(3,3,3,1,'2026-04-01 18:19:05');

-- login_sessions
INSERT INTO `login_sessions` VALUES
(1,1,'2026-04-01 18:04:13',NULL),
(2,2,'2026-04-01 18:04:13',NULL),
(3,3,'2026-04-01 18:04:13',NULL);

-- user_availability
INSERT INTO `user_availability` VALUES (1,1,'Monday',1),(2,2,'Tuesday',1),(3,3,'Wednesday',1);

-- availability_slots
INSERT INTO `availability_slots` VALUES
(1,1,'10:00:00','12:00:00'),
(2,2,'14:00:00','16:00:00'),
(3,3,'18:00:00','20:00:00');

-- user_preferences
INSERT INTO `user_preferences` VALUES
(1,1,'dark',10,'IST'),
(2,2,'light',15,'IST'),
(3,3,'dark',5,'IST');

-- user_profiles
INSERT INTO `user_profiles` VALUES
(1,1,'9999999999','IST','Bio1'),
(2,2,'8888888888','IST','Bio2'),
(3,3,'7777777777','IST','Bio3');

SET FOREIGN_KEY_CHECKS = 1;
