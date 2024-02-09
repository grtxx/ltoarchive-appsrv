-- MySQL dump 10.19  Distrib 10.3.28-MariaDB, for Linux (x86_64)
-- ------------------------------------------------------
-- Server version       10.3.28-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `appTokens`
--

DROP TABLE IF EXISTS `appTokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `appTokens` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` int(11) DEFAULT NULL,
  `token` varbinary(64) DEFAULT NULL,
  `userId` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_apptokens_appId` (`appId`),
  KEY `fk_apptokens_userId` (`userId`),
  KEY `idx_token` (`token`),
  CONSTRAINT `fk_apptokens_appId` FOREIGN KEY (`appId`) REFERENCES `apps` (`id`),
  CONSTRAINT `fk_apptokens_userId` FOREIGN KEY (`userId`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apps`
--

DROP TABLE IF EXISTS `apps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` char(100) DEFAULT NULL,
  `appSecret` varbinary(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domains`
--

DROP TABLE IF EXISTS `domains`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domains` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `isExclusiveOnTapes` tinyint(1) DEFAULT NULL,
  `isActive` tinyint(1) DEFAULT NULL,
  `copyCount` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_ArchiveDomain_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `files`
--

DROP TABLE IF EXISTS `files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `files` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domainId` int(11) DEFAULT NULL,
  `name` varchar(250) DEFAULT NULL,
  `ext` varchar(250) DEFAULT NULL,
  `parentFolderId` int(11) DEFAULT NULL,
  `hash` varchar(48) DEFAULT NULL,
  `size` bigint(20) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `isOnline` tinyint(1) DEFAULT 0,
  `isDeleted` tinyint(1) DEFAULT 0,
  `isOldVersion` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `udx_namehash` (`name`,`hash`,`parentFolderId`,`domainId`),
  KEY `archiveDomainId` (`domainId`),
  KEY `parentFolderId` (`parentFolderId`),
  KEY `ix_File_created` (`created`),
  KEY `ix_File_name` (`name`),
  KEY `ix_File_isOnline` (`isOnline`),
  KEY `ix_File_isDeleted` (`isDeleted`),
  KEY `ix_File_ext` (`ext`),
  KEY `ix_File_hash` (`hash`),
  KEY `ix_File_size` (`size`),
  KEY `idx_isOldVersion` (`isOldVersion`),
  CONSTRAINT `files_ibfk_1` FOREIGN KEY (`domainId`) REFERENCES `domains` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18863023 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `folders`
--

DROP TABLE IF EXISTS `folders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `folders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domainId` int(11) DEFAULT NULL,
  `name` varchar(250) DEFAULT NULL,
  `size` bigint(20) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `isDeleted` tinyint(1) DEFAULT NULL,
  `parentFolderId` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `archiveDomainId` (`domainId`),
  KEY `parentFolderId` (`parentFolderId`),
  KEY `ix_Folder_created` (`created`),
  KEY `ix_Folder_name` (`name`),
  KEY `ix_Folder_size` (`size`),
  KEY `ix_Folder_isDeleted` (`isDeleted`),
  CONSTRAINT `folders_ibfk_1` FOREIGN KEY (`domainId`) REFERENCES `domains` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=179428 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `jobfiles`
--

DROP TABLE IF EXISTS `jobfiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jobfiles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `jobId` int(11) DEFAULT NULL,
  `tapeId` int(11) DEFAULT NULL,
  `fileId` int(11) DEFAULT NULL,
  `dstpath` text DEFAULT NULL,
  `status` varbinary(32) DEFAULT NULL,
  `size` bigint(20) DEFAULT NULL,
  `startblock` bigint(20) DEFAULT NULL,
  `srcpath` text DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `finished` datetime DEFAULT NULL,
  `dstfs` char(250) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_jobfiles_jobId` (`jobId`),
  KEY `fk_jobfiles_tapeId` (`tapeId`),
  KEY `fk_jobfiles_fileId` (`fileId`),
  KEY `idx_status` (`status`),
  KEY `idx_startblock` (`startblock`),
  KEY `idx_created` (`created`),
  KEY `idx_finished` (`finished`),
  CONSTRAINT `fk_jobfiles_fileId` FOREIGN KEY (`fileId`) REFERENCES `files` (`id`),
  CONSTRAINT `fk_jobfiles_jobId` FOREIGN KEY (`jobId`) REFERENCES `jobs` (`id`),
  CONSTRAINT `fk_jobfiles_tapeId` FOREIGN KEY (`tapeId`) REFERENCES `tapes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=123681 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `jobs`
--

DROP TABLE IF EXISTS `jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jobs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `email` char(150) DEFAULT NULL,
  `username` char(150) DEFAULT NULL,
  `src` mediumtext DEFAULT NULL,
  `dststorage` char(64) DEFAULT NULL,
  `status` varbinary(32) DEFAULT NULL,
  `nexttask` datetime DEFAULT NULL,
  `webhook` char(250) DEFAULT NULL,
  `finished` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_created` (`created`),
  KEY `idx_status` (`status`),
  KEY `idx_nexttask` (`nexttask`),
  KEY `idx_finished` (`finished`)
) ENGINE=InnoDB AUTO_INCREMENT=143 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sessions`
--

DROP TABLE IF EXISTS `sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sessions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sessionId` char(40) DEFAULT NULL,
  `userId` int(11) DEFAULT NULL,
  `lastseen` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_sessionId` (`sessionId`),
  KEY `fk_sessions_userId` (`userId`),
  KEY `idx_lastseen` (`lastseen`),
  CONSTRAINT `fk_sessions_userId` FOREIGN KEY (`userId`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tapefolders`
--

DROP TABLE IF EXISTS `tapefolders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tapefolders` (
  `folderId` int(11) DEFAULT NULL,
  `tapeId` int(11) DEFAULT NULL,
  KEY `fk_tapefolders_folderid` (`folderId`),
  KEY `fk_tapefolders_tapeid` (`tapeId`),
  CONSTRAINT `fk_tapefolders_folderid` FOREIGN KEY (`folderId`) REFERENCES `folders` (`id`),
  CONSTRAINT `fk_tapefolders_tapeid` FOREIGN KEY (`tapeId`) REFERENCES `tapes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tapeitems`
--

DROP TABLE IF EXISTS `tapeitems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tapeitems` (
  `item_id` int(11) NOT NULL AUTO_INCREMENT,
  `tapeId` int(11) DEFAULT NULL,
  `folderId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `hash` varbinary(48) DEFAULT NULL,
  `startblock` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`item_id`),
  UNIQUE KEY `udx_hashfoldertape` (`folderId`,`tapeId`,`domainId`,`hash`),
  KEY `idx_startblock` (`startblock`),
  KEY `fk_tapeitems_tapeId` (`tapeId`),
  KEY `fk_tapeitems` (`domainId`),
  KEY `idx_hash` (`hash`),
  CONSTRAINT `fk_tapeitems` FOREIGN KEY (`domainId`) REFERENCES `domains` (`id`),
  CONSTRAINT `fk_tapeitems_folderId` FOREIGN KEY (`folderId`) REFERENCES `folders` (`id`),
  CONSTRAINT `fk_tapeitems_tapeId` FOREIGN KEY (`tapeId`) REFERENCES `tapes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19133759 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tapes`
--

DROP TABLE IF EXISTS `tapes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tapes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` varchar(8) DEFAULT NULL,
  `copyNumber` int(11) DEFAULT NULL,
  `isAvailable` tinyint(1) DEFAULT NULL,
  `isActive` tinyint(1) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `lockedBy` varbinary(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_Tape_copyNumber` (`copyNumber`)
) ENGINE=InnoDB AUTO_INCREMENT=49684 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` char(40) DEFAULT NULL,
  `fullname` char(100) DEFAULT NULL,
  `pwhash` char(64) DEFAULT NULL,
  `origin` varbinary(16) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_username` (`username`),
  KEY `idx_origin` (`origin`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

