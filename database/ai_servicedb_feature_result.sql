-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: ai_servicedb
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `feature_result`
--

DROP TABLE IF EXISTS `feature_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feature_result` (
  `num` int NOT NULL AUTO_INCREMENT,
  `userId` varchar(45) NOT NULL,
  `gender` varchar(45) NOT NULL,
  `gender_probability` decimal(4,2) NOT NULL,
  `race` varchar(45) NOT NULL,
  `race_probability` decimal(4,2) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`num`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feature_result`
--

LOCK TABLES `feature_result` WRITE;
/*!40000 ALTER TABLE `feature_result` DISABLE KEYS */;
INSERT INTO `feature_result` VALUES (1,'9dongb','남성',92.15,'아시아인',99.79,'2024-04-16 14:42:21'),(2,'9dongb','여성',99.24,'아시아인',99.65,'2024-04-16 14:43:00'),(3,'9dongb','남성',92.15,'아시아인',99.79,'2024-04-16 14:48:15'),(4,'9dongb','아시아인',99.53,'아시아인',99.53,'2024-05-09 17:36:09'),(5,'9dongb','아시아인',99.53,'아시아인',99.53,'2024-05-09 19:21:02'),(6,'9dongb','아시아인',99.53,'아시아인',99.53,'2024-05-10 03:34:58');
/*!40000 ALTER TABLE `feature_result` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-05-17 10:09:39
