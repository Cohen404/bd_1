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
-- Table structure for tb_user
-- ----------------------------
DROP TABLE IF EXISTS `tb_user`;
CREATE TABLE `tb_user` (
    `user_id` VARCHAR(64) PRIMARY KEY NOT NULL COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(64) NOT NULL COMMENT '密码',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '电话',
    `user_type` VARCHAR(10) NOT NULL DEFAULT 'user' COMMENT '用户类型: admin/user',
    `last_login` DATETIME DEFAULT NULL COMMENT '最后登录时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ----------------------------
-- Records of tb_user
-- ----------------------------
INSERT INTO `tb_user` (user_id, username, password, email, phone, user_type, created_at)
VALUES 
('admin001', 'admin', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'admin@example.com', '13800000001', 'admin', NOW()),
('user001', 'user1', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user1@example.com', '13800000002', 'user', NOW()),
('user002', 'user2', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user2@example.com', '13800000003', 'user', NOW()),
('user003', 'user3', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user3@example.com', '13800000004', 'admin', NOW());

-- ----------------------------
-- Table structure for tb_result
-- ----------------------------
DROP TABLE IF EXISTS `tb_result`;
CREATE TABLE `tb_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `result_time` datetime DEFAULT NULL COMMENT '结果计算时间',
  `stress_score` float NOT NULL COMMENT '0-100,0不普通应激，100普通应激',
  `depression_score` float NOT NULL COMMENT '0-100,0不抑郁，100抑郁',
  `anxiety_score` float NOT NULL COMMENT '0-100,0不焦虑，100焦虑',
  `report_path` varchar(255) DEFAULT NULL COMMENT '报告路径',
  `user_id` varchar(64) NOT NULL COMMENT '关联用户ID',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Table structure for tb_data
-- ----------------------------
DROP TABLE IF EXISTS `tb_data`;
CREATE TABLE `tb_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `personnel_id` varchar(64) NOT NULL COMMENT '人员id',
  `data_path` varchar(255) DEFAULT NULL COMMENT '文件路径',
  `upload_user` int(11) NOT NULL COMMENT '0/1,0是普通用户，1是管理员',
  `personnel_name` varchar(255) NOT NULL,
  `user_id` varchar(64) NOT NULL COMMENT '关联用户ID',
  `upload_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

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
(1, 0, './model/yingji/subject-1 yingji.keras', '2024-09-14 13:20:32'),
(2, 1, './model/yiyu/subject-1 yiyu.keras', '2024-09-14 13:20:41'),
(3, 2, './model/jiaolv/subject-1jiaolv.keras', '2024-09-14 13:20:47');

-- ----------------------------
-- Table structure for tb_role
-- ----------------------------
DROP TABLE IF EXISTS `tb_role`;
CREATE TABLE `tb_role` (
    `role_id` VARCHAR(64) PRIMARY KEY NOT NULL COMMENT '角色ID，主键',
    `role_name` VARCHAR(50) NOT NULL COMMENT '角色名称',
    `description` VARCHAR(255) DEFAULT NULL COMMENT '角色描述',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '角色创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色信息表';

-- ----------------------------
-- Table structure for tb_user_role
-- ----------------------------
DROP TABLE IF EXISTS `tb_user_role`;
CREATE TABLE `tb_user_role` (
    `user_id` VARCHAR(64) NOT NULL COMMENT '用户ID',
    `role_id` VARCHAR(64) NOT NULL COMMENT '角色ID',
    PRIMARY KEY (`user_id`, `role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';

-- ----------------------------
-- Table structure for tb_permission
-- ----------------------------
DROP TABLE IF EXISTS `tb_permission`;
CREATE TABLE `tb_permission` (
    `permission_id` VARCHAR(64) PRIMARY KEY NOT NULL COMMENT '权限ID，主键',
    `permission_name` VARCHAR(100) NOT NULL COMMENT '权限名称',
    `page_url` VARCHAR(255) NOT NULL COMMENT '访问的页面URL',
    `description` VARCHAR(255) DEFAULT NULL COMMENT '权限描述',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '权限创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';

-- ----------------------------
-- Table structure for tb_role_permission
-- ----------------------------
DROP TABLE IF EXISTS `tb_role_permission`;
CREATE TABLE `tb_role_permission` (
    `role_id` VARCHAR(64) NOT NULL COMMENT '角色ID',
    `permission_id` VARCHAR(64) NOT NULL COMMENT '权限ID',
    PRIMARY KEY (`role_id`, `permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关联表';

-- ----------------------------
-- Table structure for tb_system_params
-- ----------------------------
DROP TABLE IF EXISTS `tb_system_params`;
CREATE TABLE `tb_system_params` (
    `param_id` VARCHAR(64) PRIMARY KEY NOT NULL COMMENT '参数ID，主键',
    `eeg_frequency` FLOAT DEFAULT NULL COMMENT '脑电数据采样频率 (Hz)',
    `electrode_count` INT(11) DEFAULT NULL COMMENT '电极数量',
    `scale_question_num` INT(11) DEFAULT NULL COMMENT '量表问题数量',
    `model_num` INT(11) DEFAULT NULL COMMENT '系统中可用的模型数量',
    `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统参数表';

-- ----------------------------
-- Records of tb_system_params
-- ----------------------------
INSERT INTO `tb_system_params` (
    `param_id`,
    `eeg_frequency`,
    `electrode_count`,
    `scale_question_num`,
    `model_num`,
    `id`
) VALUES (
    'PARAM_001',
    500,
    64,
    40,
    3,
    1
);
