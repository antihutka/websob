CREATE TABLE `logins` (
  `login_id` int(11) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `username_id` int(11) NOT NULL,
  `client_ip` varchar(128) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `username_id` int(11) NOT NULL,
  `message_text` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `usernames` (
  `username_id` int(11) NOT NULL,
  `username` varchar(128) NOT NULL,
  `lastused` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `logins` ADD PRIMARY KEY (`login_id`);
ALTER TABLE `messages` ADD PRIMARY KEY (`id`);
ALTER TABLE `usernames` ADD PRIMARY KEY (`username_id`), ADD UNIQUE KEY `username` (`username`);

ALTER TABLE `logins` MODIFY `login_id` int(11) NOT NULL AUTO_INCREMENT;
ALTER TABLE `messages` MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
ALTER TABLE `usernames` MODIFY `username_id` int(11) NOT NULL AUTO_INCREMENT;
