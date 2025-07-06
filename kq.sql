/*
Navicat MySQL Data Transfer

Source Server         : localhost_3306
Source Server Version : 80040
Source Host           : localhost:3306
Source Database       : kq

Target Server Type    : MYSQL
Target Server Version : 80040
File Encoding         : 65001

Date: 2025-04-25 19:28:34
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `administrators`
-- ----------------------------
DROP TABLE IF EXISTS `administrators`;
CREATE TABLE `administrators` (
  `admin_id` varchar(20) NOT NULL,
  `admin_name` varchar(50) NOT NULL,
  `password` varchar(100) NOT NULL,
  `department` varchar(50) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- ----------------------------
-- Records of administrators
-- ----------------------------
INSERT INTO `administrators` VALUES ('111', '111', '111', '111', '111', '111');

-- ----------------------------
-- Table structure for `attendance_records`
-- ----------------------------
DROP TABLE IF EXISTS `attendance_records`;
CREATE TABLE `attendance_records` (
  `record_id` int NOT NULL AUTO_INCREMENT,
  `employee_id` varchar(20) NOT NULL,
  `employee_name` varchar(50) NOT NULL,
  `attendance_date` date NOT NULL,
  `attendance_time` time DEFAULT NULL,
  `departure_time` time DEFAULT NULL,
  `attendance_status` enum('on_time','late','absent','early_departure','leave') CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb3;

-- ----------------------------
-- Records of attendance_records
-- ----------------------------

-- ----------------------------
-- Table structure for `employees`
-- ----------------------------
DROP TABLE IF EXISTS `employees`;
CREATE TABLE `employees` (
  `employee_id` int NOT NULL AUTO_INCREMENT,
  `employee_name` varchar(50) NOT NULL,
  `job_title` varchar(50) NOT NULL,
  `password` varchar(100) NOT NULL,
  `department` varchar(50) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=315 DEFAULT CHARSET=utf8mb3;

-- ----------------------------
-- Records of employees
-- ----------------------------

-- ----------------------------
-- Table structure for `leave_application`
-- ----------------------------
DROP TABLE IF EXISTS `leave_application`;
CREATE TABLE `leave_application` (
  `id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int NOT NULL,
  `employee_name` varchar(255) NOT NULL,
  `department` varchar(255) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `leave_type` enum('病假','年假','事假','产假','其他') NOT NULL DEFAULT '事假',
  `leave_days` int NOT NULL,
  `leave_reason` text,
  `status` enum('待审批','已通过','已拒绝','已批准') NOT NULL DEFAULT '待审批',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=249 DEFAULT CHARSET=utf8mb3;

-- ----------------------------
-- Records of leave_application
-- ----------------------------

-- ----------------------------
-- Table structure for `surgery_notification`
-- ----------------------------
DROP TABLE IF EXISTS `surgery_notification`;
CREATE TABLE `surgery_notification` (
  `notification_id` int NOT NULL AUTO_INCREMENT,
  `surgery_date` date NOT NULL,
  `surgery_time` time NOT NULL,
  `department` varchar(50) NOT NULL,
  `operating_room` varchar(50) NOT NULL,
  `patient_name` varchar(50) NOT NULL,
  `surgery_type` varchar(50) NOT NULL,
  `responsible_doctor_id` int NOT NULL,
  `notes` text,
  PRIMARY KEY (`notification_id`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb3;

-- ----------------------------
-- Records of surgery_notification
-- ----------------------------
