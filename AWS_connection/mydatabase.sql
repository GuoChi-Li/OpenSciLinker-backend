-- MySQL dump 10.13  Distrib 5.7.24, for osx10.9 (x86_64)
--
-- Host: localhost    Database: mydatabase
-- ------------------------------------------------------
-- Server version	8.1.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `text` text NOT NULL,
  `timestamp` datetime NOT NULL,
  `user_email` varchar(120) NOT NULL,
  `post_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_email` (`user_email`),
  KEY `post_id` (`post_id`),
  KEY `ix_comments_id` (`id`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`user_email`) REFERENCES `users` (`email`),
  CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (1,'good!','2023-10-08 10:59:16','ivy23090611@gmail.com',1),(2,'bad!','2023-10-08 10:59:30','ton731@gmail.com',1),(3,'cool!','2023-10-08 11:01:14','user2@gmail.com',1),(4,'Ugh!','2023-10-08 11:01:29','user2@gmail.com',2);
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `likes`
--

DROP TABLE IF EXISTS `likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `likes` (
  `user_email` varchar(120) NOT NULL,
  `post_id` int NOT NULL,
  PRIMARY KEY (`user_email`,`post_id`),
  KEY `post_id` (`post_id`),
  CONSTRAINT `likes_ibfk_1` FOREIGN KEY (`user_email`) REFERENCES `users` (`email`),
  CONSTRAINT `likes_ibfk_2` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `likes`
--

LOCK TABLES `likes` WRITE;
/*!40000 ALTER TABLE `likes` DISABLE KEYS */;
INSERT INTO `likes` VALUES ('ton731@gmail.com',2);
/*!40000 ALTER TABLE `likes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `post_tags`
--

DROP TABLE IF EXISTS `post_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `post_tags` (
  `post_id` int NOT NULL,
  `tag_name` varchar(255) NOT NULL,
  PRIMARY KEY (`post_id`,`tag_name`),
  KEY `tag_name` (`tag_name`),
  CONSTRAINT `post_tags_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`),
  CONSTRAINT `post_tags_ibfk_2` FOREIGN KEY (`tag_name`) REFERENCES `tags` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `post_tags`
--

LOCK TABLES `post_tags` WRITE;
/*!40000 ALTER TABLE `post_tags` DISABLE KEYS */;
INSERT INTO `post_tags` VALUES (1,'Arts'),(2,'Arts'),(3,'Civil Engineering'),(4,'Civil Engineering'),(2,'Computer Science');
/*!40000 ALTER TABLE `post_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts`
--

DROP TABLE IF EXISTS `posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `posts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `timestamp` datetime NOT NULL,
  `author_email` varchar(120) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `author_email` (`author_email`),
  KEY `ix_posts_id` (`id`),
  CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`author_email`) REFERENCES `users` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts`
--

LOCK TABLES `posts` WRITE;
/*!40000 ALTER TABLE `posts` DISABLE KEYS */;
INSERT INTO `posts` VALUES (1,'Test Project','I am Tony, who are you.','2023-10-08 02:23:20','ton731@gmail.com'),(2,'Another Project','I ssss Tony, who are you.','2023-10-08 02:23:20','ton731@gmail.com'),(3,'BIM','Bim good','2023-10-08 05:52:05','ton731@gmail.com'),(4,'David Chen','good good','2023-10-08 05:52:05','ton731@gmail.com');
/*!40000 ALTER TABLE `posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_tags_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES (1,'Arts'),(3,'Civil Engineering'),(2,'Computer Science');
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `username` varchar(20) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password` varchar(60) NOT NULL,
  PRIMARY KEY (`email`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('SjalBlge','bGDtbhHr@example.com','$2b$12$kjceUyUSyctJtSc4SYIh/.QiPo721cUTVS8V0f4Jobkxa8WWc9xlK'),('rPWsrUPn','eziYBhzi@example.com','$2b$12$LVqRfkoHNQ60FSl/3AqVkuZp54JhpZYAmVUfNDt49xINOCXQFFlT.'),('xkICvtHr','iPzGxGPy@example.com','$2b$12$C/Ke1smrT9HT0Rh7VJQRQewAlXGDONCK9FoVbmFY3nY.zDulXUOo2'),('Ivy Huang','ivy23090611@gmail.com','$2b$12$HlqKG85FSnsmtxKEffg5EO9URkZAG70tvjDU64PgGQh81TN.cKFDm'),('LNciQtKx','JjgDRXFa@example.com','$2b$12$dJrwurSW3UlKFeZ33nHm7uDU./tu0BzZjHpJkiUOAeOGC3rneM046'),('aTqPRMFj','LyPoeXtV@example.com','$2b$12$1HnorTht7EO.IGwhjP8uc.WJkOogqtatXmIZw3Axfkd9bNpa/XnUi'),('Tony Chou','ton731@gmail.com','$2b$12$dWLhiuajJz0Gws3UiSkoV.qv0bWr5SKxl0oNgYDSS4e5pdvglrc7e'),('FRrraRgn','ttWzyQDg@example.com','$2b$12$pXa2J.UCULSvBiUVDLTqUe6GVvCma18/.XD0nHcv5WQlCHWor/Z9u'),('agjBVSEg','UkOfbDjn@example.com','$2b$12$LFzaZ2PZN8gUNVmqJhwVX.WGX7IiWaR5ZarROSH04atc1EvtQyx/e'),('tst user1','user1@gmail.com','$2b$12$8oD312j3RNNq7MDr8LzLdeeq/owM5nrz1TOczloYbcsuIQpcfFT4W'),('22tst user1','user2@gmail.com','$2b$12$cX61Pd1X.JP2x.0mf1/aSO4QKZI1TardTaR4oztP6oShoBOjB7WXC'),('22tst user12','user3@gmail.com','$2b$12$Gr3fwkEzk52E6pub3xuHberaQUMzG.ER14vbP0Y.c1cKi3toSD6TC'),('flkhgskhgk','user5@gmail.com','$2b$12$E25F.jocU/bLp3sV8t/OCOq/FZfewTcO5QjkE5JZtotkDPK/yZsBS'),('gryerjtrjyukt','user6@gmail.com','$2b$12$pD6CzmuPh3MVZkOXhv4gt.BBOrQScI5P27x3TKGHfEGg3yjeP9LeW'),('OinPgEiU','wPxbDjPr@example.com','$2b$12$00nX515ASdqOalCdemDal.lj0ZipcIYyKljYhCg22Q262mlou/p1a'),('GmOjatuQ','yhJBVhJG@example.com','$2b$12$9DhclAbpbM9zwb6KtWndd.jECfF6nWVQEy/Z/SNjo2ztJV4vDA6cy'),('WsQZqSla','yXLvEIBD@example.com','$2b$12$hbkiLLSmY/epgrpbVoN3UezCqXXstuMDlnacBO2arDOZrs71ecFbu');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-10-08 14:34:02
