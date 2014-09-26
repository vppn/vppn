CREATE DATABASE vppn;
CREATE TABLE `vppn`.`vppn` (
  `userid` varchar(64) CHARACTER SET latin1 NOT NULL,
  `password` varchar(64) CHARACTER SET latin1 DEFAULT NULL,
  `expired` date DEFAULT NULL,
  `trialCount` int(11) NOT NULL DEFAULT '1',
  `memo` text CHARACTER SET latin1,
  `blocked` int(11) DEFAULT '0',
  `createdate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `updatedate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`userid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;