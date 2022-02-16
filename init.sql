DROP TABLE IF EXISTS `user_settings`;
CREATE TABLE IF NOT EXISTS `user_settings` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `created_at` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  `chat_id` INT(12) NOT NULL,
  `name` VARCHAR(32) NOT NULL,
  `timezone` VARCHAR(32) NOT NULL
);
CREATE INDEX us_chat_id_idx ON `user_settings` (`chat_id`);

DROP TABLE IF EXISTS `notifications`;
CREATE TABLE IF NOT EXISTS `notifications` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `created_at` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  `chat_id` INT(12) NOT NULL,
  `name` VARCHAR(32) NOT NULL,
  `time` CHAR(5) NOT NULL,
  `dosage` VARCHAR(32) NOT NULL,

  `enabled` BOOLEAN NOT NULL
);
CREATE INDEX nfs_chat_id_idx ON `notifications` (`chat_id`);

DROP TABLE IF EXISTS `history`;
CREATE TABLE IF NOT EXISTS `history` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `created_at` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  `chat_id` INT(12) NOT NULL,
  `name` VARCHAR(32) NOT NULL,
  `time` CHAR(5) NOT NULL,
  `dosage` VARCHAR(32) NOT NULL
);
CREATE INDEX hst_chat_id_idx ON `history` (`chat_id`);
