/*
 Navicat Premium Dump SQL

 Source Server         : test
 Source Server Type    : MySQL
 Source Server Version : 50726 (5.7.26)
 Source Host           : localhost:3306
 Source Schema         : sql_model

 Target Server Type    : MySQL
 Target Server Version : 50726 (5.7.26)
 File Encoding         : 65001

 Date: 06/08/2024 11:31:19
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tb_data
-- ----------------------------
DROP TABLE IF EXISTS `tb_data`;
CREATE TABLE `tb_data`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `personnel_id` int(11) NOT NULL COMMENT '人员id',
  `data_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件路径',
  `upload_user` int(11) NOT NULL COMMENT '0/1,0是普通用户，1是管理员',
  `personnel_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of tb_data
-- ----------------------------
INSERT INTO `tb_data` VALUES (2, 2, '../data/2_lisi', 1, 'lisi');
INSERT INTO `tb_data` VALUES (3, 3, '../data/3_wangwu', 0, 'wangwu');
INSERT INTO `tb_data` VALUES (4, 2, '../data/2_zhangsan', 0, 'zhangsan');

-- ----------------------------
-- Table structure for tb_model
-- ----------------------------
DROP TABLE IF EXISTS `tb_model`;
CREATE TABLE `tb_model`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `model_type` int(11) NOT NULL COMMENT '0普通应激模型，1抑郁评估模型，2焦虑评估模型',
  `model_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '模型路径',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of tb_model
-- ----------------------------

-- ----------------------------
-- Table structure for tb_parameters
-- ----------------------------
DROP TABLE IF EXISTS `tb_parameters`;
CREATE TABLE `tb_parameters`  (
  `eeg_location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '脑电采集指标位置',
  `frequency` int(11) NULL DEFAULT NULL COMMENT '频率',
  `electrode_count` int(11) NULL DEFAULT NULL COMMENT '电极数',
  `data_format` int(11) NULL DEFAULT NULL COMMENT '数据采集格式'
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of tb_parameters
-- ----------------------------

-- ----------------------------
-- Table structure for tb_result
-- ----------------------------
DROP TABLE IF EXISTS `tb_result`;
CREATE TABLE `tb_result`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `result_time` datetime NULL DEFAULT NULL COMMENT '结果计算时间',
  `result_1` int(11) NOT NULL COMMENT '0/1,0不普通应激，1普通应激',
  `result_2` int(11) NOT NULL COMMENT '0/1,0不抑郁，1抑郁',
  `result_3` int(11) NOT NULL COMMENT '0/1,0不焦虑，1焦虑',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of tb_result
-- ----------------------------
INSERT INTO `tb_result` VALUES (1, '2024-08-06 09:57:21', 1, 1, 1);

-- ----------------------------
-- Table structure for tb_user
-- ----------------------------
DROP TABLE IF EXISTS `tb_user`;
CREATE TABLE `tb_user`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pwd` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `user_type` int(11) NOT NULL COMMENT '0/1,0是普通用户，1是管理员',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of tb_user
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
