/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50726
Source Host           : localhost:3306
Source Database       : sql_model

Target Server Type    : MYSQL
Target Server Version : 50726
File Encoding         : 65001

Date: 2024-09-19 13:20:34
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
SET GLOBAL interactive_timeout = 28800;
SET GLOBAL wait_timeout = 28800;

-- ----------------------------
-- Table structure for tb_data
-- ----------------------------
DROP TABLE IF EXISTS `tb_data`;
CREATE TABLE `tb_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `personnel_id` int(11) NOT NULL COMMENT '人员id',
  `data_path` varchar(255) DEFAULT NULL COMMENT '文件路径',
  `upload_user` int(11) NOT NULL COMMENT '0/1,0是普通用户，1是管理员',
  `personnel_name` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of tb_data
-- ----------------------------
INSERT INTO `tb_data` (`id`, `personnel_id`, `data_path`, `upload_user`, `personnel_name`, `user_id`) VALUES 
(2, 4, '../data/000004_test', 0, 'test', 1),
(3, 9, '../data/000009_yiyu6', 1, 'yiyu6', 1),
(4, 10, '../data/000010_yiyu5', 1, 'yiyu5', 1),
(5, 11, '../data/000011_yiyu4', 1, 'yiyu4', 1),
(6, 12, '../data/000012_yiyu3', 1, 'yiyu3', 1),
(7, 13, '../data/000013_yiyu2', 1, 'yiyu2', 1),
(8, 14, '../data/000014_jiaolv2', 1, 'jiaolv2', 1),
(9, 7, '../data/000007_yiyu1', 1, 'yiyu1', 1),
(10, 8, '../data/000008_jiaolv1', 1, 'jiaolv1', 1),
(11, 15, '../data/000015_yingji1', 1, 'yingji1', 1);

-- ----------------------------
-- Table structure for tb_model
-- ----------------------------
DROP TABLE IF EXISTS `tb_model`;
CREATE TABLE `tb_model` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `model_type` int(11) NOT NULL COMMENT '0普通应激模型，1抑郁评估模型，2焦虑评估模型',
  `model_path` varchar(255) DEFAULT NULL COMMENT '模型路径',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of tb_model
-- ----------------------------
INSERT INTO `tb_model` (`id`, `model_type`, `model_path`, `create_time`) VALUES 
(1, 0, '..\\..\\..\\..\\..\\subject-1 yingji.keras', '2024-09-14 13:20:32'),
(2, 1, '..\\..\\..\\..\\..\\subject-1 yiyu.keras', '2024-09-14 13:20:41'),
(3, 2, '..\\..\\..\\..\\..\\subject-1 jiaolv.keras', '2024-09-14 13:20:47');

-- ----------------------------
-- Table structure for tb_parameters
-- ----------------------------
DROP TABLE IF EXISTS `tb_parameters`;
CREATE TABLE `tb_parameters` (
  `eeg_location` varchar(255) DEFAULT NULL COMMENT '脑电采集指标位置',
  `frequency` int(11) DEFAULT NULL COMMENT '频率',
  `electrode_count` int(11) DEFAULT NULL COMMENT '电极数',
  `data_format` int(11) DEFAULT NULL COMMENT '数据采集格式',
  `id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Table structure for tb_result
-- ----------------------------
DROP TABLE IF EXISTS `tb_result`;
CREATE TABLE `tb_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `result_time` datetime DEFAULT NULL COMMENT '结果计算时间',
  `result_1` int(11) NOT NULL COMMENT '0/1,0不普通应激，1普通应激',
  `result_2` int(11) NOT NULL COMMENT '0/1,0不抑郁，1抑郁',
  `result_3` int(11) NOT NULL COMMENT '0/1,0不焦虑，1焦虑',
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of tb_result
-- ----------------------------
INSERT INTO `tb_result` (`id`, `result_time`, `result_1`, `result_2`, `result_3`, `user_id`) VALUES 
(3, '2024-09-14 13:21:25', 1, 1, 0, 1),
(4, '2024-09-14 13:21:57', 1, 1, 0, 1),
(5, '2024-09-14 13:21:02', 1, 1, 0, 1),
(6, '2024-09-14 13:22:16', 1, 1, 0, 1),
(7, '2024-09-14 13:22:53', 1, 1, 0, 1),
(8, '2024-09-14 13:26:55', 1, 1, 1, 1),
(9, '2024-09-14 13:23:45', 1, 1, 0, 1),
(10, '2024-09-14 13:29:43', 1, 1, 1, 1),
(11, '2024-09-14 13:59:22', 1, 0, 0, 1);

-- ----------------------------
-- Table structure for tb_user
-- ----------------------------
DROP TABLE IF EXISTS `tb_user`;
CREATE TABLE `tb_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pwd` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `user_type` int(11) NOT NULL COMMENT '0/1,0是普通用户，1是管理员',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of tb_user
-- ----------------------------
INSERT INTO `tb_user` (`id`, `pwd`, `name`, `user_type`) VALUES 
(1, '123', 'admin', 1),
(2, '1234', '123', 0),
(3, '111', '111', 0),
(4, '222', '222', 1);