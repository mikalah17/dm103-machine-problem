-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: food_ordering_bpm
-- ------------------------------------------------------
-- Server version	8.0.46

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
-- Table structure for table `menu_items`
--

DROP TABLE IF EXISTS `menu_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `category` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_order` int NOT NULL DEFAULT '0',
  `is_available` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_menu_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_items`
--

LOCK TABLES `menu_items` WRITE;
/*!40000 ALTER TABLE `menu_items` DISABLE KEYS */;
INSERT INTO `menu_items` VALUES (1,'Chicken Meal',120.00,'Meals',1,1),(2,'Pork Adobo Meal',110.00,'Meals',2,1),(3,'Burger Steak Meal',100.00,'Meals',3,1),(4,'Spaghetti',85.00,'Meals',4,1),(5,'French Fries',50.00,'Sides',5,1),(6,'Siomai (4 pcs)',45.00,'Sides',6,1),(7,'Iced Tea',35.00,'Drinks',7,1),(8,'Softdrink',30.00,'Drinks',8,1),(9,'Bottled Water',20.00,'Drinks',9,1);
/*!40000 ALTER TABLE `menu_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `menu_item_id` int DEFAULT NULL,
  `item_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `quantity` int NOT NULL,
  `note` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `menu_item_id` (`menu_item_id`),
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`menu_item_id`) REFERENCES `menu_items` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,1,1,'Chicken Meal',120.00,1,NULL),(2,1,2,'Pork Adobo Meal',110.00,1,NULL),(3,2,1,'Chicken Meal',120.00,1,NULL),(4,2,4,'Spaghetti',85.00,1,NULL),(5,2,6,'Siomai (4 pcs)',45.00,1,NULL),(6,2,7,'Iced Tea',35.00,1,NULL),(7,3,1,'Chicken Meal',120.00,1,NULL),(8,3,2,'Pork Adobo Meal',110.00,1,NULL),(9,3,3,'Burger Steak Meal',100.00,1,NULL),(10,3,9,'Bottled Water',20.00,1,NULL),(11,3,8,'Softdrink',30.00,1,NULL),(12,4,2,'Pork Adobo Meal',110.00,1,NULL),(13,4,6,'Siomai (4 pcs)',45.00,1,NULL),(14,4,9,'Bottled Water',20.00,1,NULL),(15,5,6,'Siomai (4 pcs)',45.00,1,NULL),(16,5,3,'Burger Steak Meal',100.00,1,NULL),(17,5,9,'Bottled Water',20.00,1,NULL),(18,6,3,'Burger Steak Meal',100.00,1,NULL),(19,7,1,'Chicken Meal',120.00,1,NULL),(20,7,6,'Siomai (4 pcs)',45.00,1,NULL),(21,7,9,'Bottled Water',20.00,1,NULL),(22,8,1,'Chicken Meal',120.00,1,NULL),(23,8,6,'Siomai (4 pcs)',45.00,1,NULL),(24,8,9,'Bottled Water',20.00,1,NULL);
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_status_log`
--

DROP TABLE IF EXISTS `order_status_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_status_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `remarks` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `changed_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `order_status_log_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_status_log`
--

LOCK TABLES `order_status_log` WRITE;
/*!40000 ALTER TABLE `order_status_log` DISABLE KEYS */;
INSERT INTO `order_status_log` VALUES (1,1,'ORDER PLACED','2 item(s), total 230.00','2026-10-05 14:53:49'),(2,1,'PENDING PAYMENT','Waiting for payment','2026-10-05 14:53:49'),(3,1,'CONFIRMED','Paid via Cash','2026-10-05 14:54:02'),(4,1,'PREPARING',NULL,'2026-10-05 14:56:15'),(5,1,'READY',NULL,'2026-10-05 14:56:16'),(6,1,'COMPLETED',NULL,'2026-10-05 14:56:21'),(7,2,'ORDER PLACED','4 item(s), total 285.00','2026-10-05 14:56:48'),(8,2,'CONFIRMED','Paid via Maya','2026-10-05 14:56:48'),(9,2,'PREPARING',NULL,'2026-10-05 14:56:50'),(10,2,'READY',NULL,'2026-10-05 14:56:58'),(11,2,'COMPLETED',NULL,'2026-10-05 14:56:59'),(12,3,'ORDER PLACED','5 item(s), total 380.00','2026-10-05 15:07:35'),(13,3,'CONFIRMED','Paid via Cash','2026-10-05 15:07:35'),(14,3,'PREPARING',NULL,'2026-10-05 15:07:37'),(15,3,'READY',NULL,'2026-10-05 15:07:39'),(16,3,'COMPLETED',NULL,'2026-10-05 15:07:57'),(17,4,'ORDER PLACED','3 item(s), total 175.00','2026-10-05 15:10:27'),(18,4,'PENDING PAYMENT','Waiting for payment','2026-10-05 15:10:27'),(19,5,'ORDER PLACED','3 item(s), total 165.00','2026-10-05 15:40:07'),(20,5,'CONFIRMED','Paid via Cash','2026-10-05 15:40:07'),(21,5,'PREPARING',NULL,'2026-10-05 15:40:24'),(22,5,'READY',NULL,'2026-10-05 15:40:52'),(23,5,'COMPLETED',NULL,'2026-10-05 15:40:56'),(24,4,'CONFIRMED','Paid via Cash','2026-10-05 15:41:02'),(25,4,'PREPARING',NULL,'2026-10-05 15:41:03'),(26,4,'READY',NULL,'2026-10-05 15:41:04'),(27,4,'COMPLETED',NULL,'2026-10-05 15:41:04'),(28,6,'ORDER PLACED','1 item(s), total 100.00','2026-10-05 15:50:59'),(29,6,'CONFIRMED','Paid via Cash','2026-10-05 15:50:59'),(30,6,'PREPARING',NULL,'2026-10-05 15:51:02'),(31,6,'READY',NULL,'2026-10-05 16:01:00'),(32,6,'COMPLETED',NULL,'2026-10-05 16:01:01'),(33,7,'ORDER PLACED','3 item(s), total 185.00','2026-10-05 18:44:37'),(34,7,'CONFIRMED','Paid via Cash','2026-10-05 18:44:37'),(35,7,'PREPARING',NULL,'2026-10-05 18:44:58'),(36,7,'READY',NULL,'2026-10-05 18:45:02'),(37,7,'COMPLETED',NULL,'2026-10-05 18:45:03'),(38,8,'ORDER PLACED','3 item(s), total 185.00','2026-10-05 18:57:14'),(39,8,'PENDING PAYMENT','Waiting for payment','2026-10-05 18:57:14'),(40,8,'CONFIRMED','Paid via Cash','2026-10-05 18:57:20'),(41,8,'PREPARING',NULL,'2026-10-05 18:57:25'),(42,8,'READY',NULL,'2026-10-05 18:57:27'),(43,8,'COMPLETED',NULL,'2026-10-05 18:57:29');
/*!40000 ALTER TABLE `order_status_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `payment_method` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `payment_status` enum('UNPAID','PAID') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'UNPAID',
  `status` enum('PENDING PAYMENT','CONFIRMED','PREPARING','READY','COMPLETED') COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `paid_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,'maria',230.00,'Cash','PAID','COMPLETED','2026-10-05 14:53:49','2026-10-05 14:54:02','2026-10-05 14:56:22'),(2,'a',285.00,'Maya','PAID','COMPLETED','2026-10-05 14:56:48','2026-10-05 14:56:48','2026-10-05 14:57:00'),(3,'Maria',380.00,'Cash','PAID','COMPLETED','2026-10-05 15:07:35','2026-10-05 15:07:36','2026-10-05 15:07:57'),(4,'a',175.00,'Cash','PAID','COMPLETED','2026-10-05 15:10:27','2026-10-05 15:41:02','2026-10-05 15:41:05'),(5,'b',165.00,'Cash','PAID','COMPLETED','2026-10-05 15:40:07','2026-10-05 15:40:07','2026-10-05 15:40:56'),(6,'c',100.00,'Cash','PAID','COMPLETED','2026-10-05 15:50:59','2026-10-05 15:50:59','2026-10-05 16:01:02'),(7,'Beverly',185.00,'Cash','PAID','COMPLETED','2026-10-05 18:44:37','2026-10-05 18:44:37','2026-10-05 18:45:03'),(8,'Rio',185.00,'Cash','PAID','COMPLETED','2026-10-05 18:57:14','2026-10-05 18:57:20','2026-10-05 18:57:29');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-05 19:15:15
