CREATE TABLE users (
  id INT PRIMARY KEY,
  name VARCHAR(255)
);

CREATE TABLE `tbl_user_lbase_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `lbaseid` int(11) NOT NULL,
  `module_id` varchar(255) NOT NULL,
  `visited` enum('0','1') NOT NULL,
  `completed` enum('0','1') NOT NULL,
  `progress` int(10) NOT NULL,
  `updated` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `rowkey` bigint(20) GENERATED ALWAYS AS (cast(unix_timestamp(`rowkeytime`) as signed)) VIRTUAL,
  `rowkeytime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `rowkeynum` bigint(20) GENERATED ALWAYS AS (cast(unix_timestamp(`rowkeytime`) as signed)) VIRTUAL,
  PRIMARY KEY (`id`,`lbaseid`),
  UNIQUE KEY `unique_row_param` (`user_id`,`lbaseid`,`module_id`)
)