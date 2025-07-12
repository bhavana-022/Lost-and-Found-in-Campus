-- MySQL dump 10.13  Distrib 9.3.0, for Win64 (x86_64)
--
-- Host: localhost    Database: lost_and_found_db
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `claims`
--

DROP TABLE IF EXISTS `claims`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `claims` (
  `id` int NOT NULL AUTO_INCREMENT,
  `item_id` int NOT NULL,
  `claimer_user_id` int NOT NULL,
  `claim_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(20) DEFAULT 'pending',
  `reporter_confirmed` tinyint(1) DEFAULT '0',
  `claimer_confirmed` tinyint(1) DEFAULT '0',
  `closed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `item_id` (`item_id`),
  KEY `claimer_user_id` (`claimer_user_id`),
  CONSTRAINT `claims_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `lost_items` (`id`),
  CONSTRAINT `claims_ibfk_2` FOREIGN KEY (`claimer_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `claims`
--

LOCK TABLES `claims` WRITE;
/*!40000 ALTER TABLE `claims` DISABLE KEYS */;
/*!40000 ALTER TABLE `claims` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lost_item`
--

DROP TABLE IF EXISTS `lost_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lost_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `roll` varchar(50) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `product` varchar(100) DEFAULT NULL,
  `department` varchar(50) DEFAULT NULL,
  `image` varchar(120) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'lost',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lost_item`
--

LOCK TABLES `lost_item` WRITE;
/*!40000 ALTER TABLE `lost_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `lost_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lost_items`
--

DROP TABLE IF EXISTS `lost_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lost_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `roll_no` varchar(20) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `product_name` varchar(100) DEFAULT NULL,
  `department` varchar(50) DEFAULT NULL,
  `image_filename` varchar(255) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `location_found` varchar(255) DEFAULT NULL,
  `description` text,
  `verification_status` enum('unverified','verified') DEFAULT 'unverified',
  `archived` tinyint(1) NOT NULL DEFAULT '0',
  `handover_status` varchar(50) DEFAULT NULL,
  `claimed_by` varchar(100) DEFAULT NULL,
  `received_confirmed_by_reporter` tinyint(1) DEFAULT '0',
  `handed_confirmed_by_finder` tinyint(1) DEFAULT '0',
  `finder_user_id` int DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_finder_user` (`finder_user_id`),
  CONSTRAINT `fk_finder_user` FOREIGN KEY (`finder_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lost_items`
--

LOCK TABLES `lost_items` WRITE;
/*!40000 ALTER TABLE `lost_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `lost_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'gopi bhavana rao','gopibhavana31@gmail.com','scrypt:32768:8:1$JMRVOGfnfgaRyliT$aee3c57b8596270953f5a5438bc4eefd54baeff7e966a5fc4005fb9c40920e73b2ceba324e913d9955b1182f3081818ba6f0279d4a6fc5eea7412e82897ee4f0'),(2,'laya','glayarao2244@gmail.com','scrypt:32768:8:1$jVMIsiHrkjUs6jKj$d407f7e191bd3ca565573af92a71077dd06d56ded430da705ec9284d9a39fdcff170d3e5eaa6206943d383bc03e504e33082f059d2c717b7a572c395ef507d68'),(3,'gopi','gopitv456@gmail.com','scrypt:32768:8:1$DRM8XzxmKQTGy3Ab$eb8a85e5e0cb65bc8f841f573f23bec412420cc4426a1766dbe4ddb9f9aea2faba228b2880a741a4367b535d68c94126af32051bdf774bb2dea5e1cc016f285a');
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

-- Dump completed on 2025-05-27 23:21:51
