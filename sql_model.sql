/*
PostgreSQL Database Export

Target Server Type    : PostgreSQL
Target Server Version : 12.0
File Encoding         : UTF-8

Date: 2024-09-19 13:20:34
*/

-- ----------------------------
-- Table structure for tb_user
-- ----------------------------
DROP TABLE IF EXISTS tb_user;
CREATE TABLE tb_user (
    user_id VARCHAR(64) PRIMARY KEY NOT NULL,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(64) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    user_type VARCHAR(10) NOT NULL DEFAULT 'user',
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE tb_user IS '用户表';
COMMENT ON COLUMN tb_user.user_id IS '用户ID';
COMMENT ON COLUMN tb_user.username IS '用户名';
COMMENT ON COLUMN tb_user.password IS '密码';
COMMENT ON COLUMN tb_user.email IS '邮箱';
COMMENT ON COLUMN tb_user.phone IS '电话';
COMMENT ON COLUMN tb_user.user_type IS '用户类型: admin/user';
COMMENT ON COLUMN tb_user.last_login IS '最后登录时间';
COMMENT ON COLUMN tb_user.created_at IS '创建时间';
COMMENT ON COLUMN tb_user.updated_at IS '更新时间';

-- ----------------------------
-- Records of tb_user
-- ----------------------------
INSERT INTO tb_user (user_id, username, password, email, phone, user_type, created_at)
VALUES 
('admin001', 'admin', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'admin@example.com', '13800000001', 'admin', CURRENT_TIMESTAMP),
('user001', 'user1', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user1@example.com', '13800000002', 'user', CURRENT_TIMESTAMP),
('user002', 'user2', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user2@example.com', '13800000003', 'user', CURRENT_TIMESTAMP),
('user003', 'user3', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user3@example.com', '13800000004', 'admin', CURRENT_TIMESTAMP);

-- ----------------------------
-- Table structure for tb_result
-- ----------------------------
DROP TABLE IF EXISTS tb_result;
CREATE TABLE tb_result (
  id SERIAL PRIMARY KEY,
  result_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  stress_score FLOAT NOT NULL,
  depression_score FLOAT NOT NULL,
  anxiety_score FLOAT NOT NULL,
  report_path VARCHAR(255),
  user_id VARCHAR(64) NOT NULL
);
COMMENT ON TABLE tb_result IS '结果表';
COMMENT ON COLUMN tb_result.id IS 'ID';
COMMENT ON COLUMN tb_result.result_time IS '结果计算时间';
COMMENT ON COLUMN tb_result.stress_score IS '0-100,0不普通应激，100普通应激';
COMMENT ON COLUMN tb_result.depression_score IS '0-100,0不抑郁，100抑郁';
COMMENT ON COLUMN tb_result.anxiety_score IS '0-100,0不焦虑，100焦虑';
COMMENT ON COLUMN tb_result.report_path IS '报告路径';
COMMENT ON COLUMN tb_result.user_id IS '关联用户ID';

-- ----------------------------
-- Table structure for tb_data
-- ----------------------------
DROP TABLE IF EXISTS tb_data;
CREATE TABLE tb_data (
    id SERIAL PRIMARY KEY,
    personnel_id VARCHAR(64) NOT NULL,
    data_path VARCHAR(255),
    upload_user INTEGER NOT NULL,
    personnel_name VARCHAR(255) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE tb_data IS '数据表';
COMMENT ON COLUMN tb_data.personnel_id IS '人员id';
COMMENT ON COLUMN tb_data.data_path IS '文件路径';
COMMENT ON COLUMN tb_data.upload_user IS '0/1,0是普通用户，1是管理员';
COMMENT ON COLUMN tb_data.personnel_name IS '人员姓名';
COMMENT ON COLUMN tb_data.user_id IS '关联用户ID';
COMMENT ON COLUMN tb_data.upload_time IS '上传时间';

-- ----------------------------
-- Table structure for tb_model
-- ----------------------------
DROP TABLE IF EXISTS tb_model;
CREATE TABLE tb_model (
    id SERIAL PRIMARY KEY,
    model_type INTEGER NOT NULL,
    model_path VARCHAR(255),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE tb_model IS '模型表';
COMMENT ON COLUMN tb_model.model_type IS '0普通应激模型，1抑郁评估模型，2焦虑评估模型';
COMMENT ON COLUMN tb_model.model_path IS '模型路径';
COMMENT ON COLUMN tb_model.create_time IS '创建时间';

-- ----------------------------
-- Records of tb_model
-- ----------------------------
INSERT INTO tb_model (model_type, model_path, create_time) VALUES 
(0, './model/yingji/subject-1 yingji.keras', CURRENT_TIMESTAMP),
(1, './model/yiyu/subject-1 yiyu.keras', CURRENT_TIMESTAMP),
(2, './model/jiaolv/subject-1jiaolv.keras', CURRENT_TIMESTAMP);

-- ----------------------------
-- Table structure for tb_role
-- ----------------------------
DROP TABLE IF EXISTS tb_role;
CREATE TABLE tb_role (
    role_id VARCHAR(64) PRIMARY KEY NOT NULL,
    role_name VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE tb_role IS '角色信息表';
COMMENT ON COLUMN tb_role.role_id IS '角色ID，主键';
COMMENT ON COLUMN tb_role.role_name IS '角色名称';
COMMENT ON COLUMN tb_role.description IS '角色描述';
COMMENT ON COLUMN tb_role.created_at IS '角色创建时间';

-- ----------------------------
-- Table structure for tb_user_role
-- ----------------------------
DROP TABLE IF EXISTS tb_user_role;
CREATE TABLE tb_user_role (
    user_id VARCHAR(64) NOT NULL,
    role_id VARCHAR(64) NOT NULL,
    PRIMARY KEY (user_id, role_id)
);
COMMENT ON TABLE tb_user_role IS '用户角色关联表';
COMMENT ON COLUMN tb_user_role.user_id IS '用户ID';
COMMENT ON COLUMN tb_user_role.role_id IS '角色ID';

-- ----------------------------
-- Table structure for tb_permission
-- ----------------------------
DROP TABLE IF EXISTS tb_permission;
CREATE TABLE tb_permission (
    permission_id VARCHAR(64) PRIMARY KEY NOT NULL,
    permission_name VARCHAR(100) NOT NULL,
    page_url VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE tb_permission IS '权限表';
COMMENT ON COLUMN tb_permission.permission_id IS '权限ID，主键';
COMMENT ON COLUMN tb_permission.permission_name IS '权限名称';
COMMENT ON COLUMN tb_permission.page_url IS '访问的页面URL';
COMMENT ON COLUMN tb_permission.description IS '权限描述';
COMMENT ON COLUMN tb_permission.created_at IS '权限创建时间';

-- ----------------------------
-- Table structure for tb_role_permission
-- ----------------------------
DROP TABLE IF EXISTS tb_role_permission;
CREATE TABLE tb_role_permission (
    role_id VARCHAR(64) NOT NULL,
    permission_id VARCHAR(64) NOT NULL,
    PRIMARY KEY (role_id, permission_id)
);
COMMENT ON TABLE tb_role_permission IS '角色权限关联表';
COMMENT ON COLUMN tb_role_permission.role_id IS '角色ID';
COMMENT ON COLUMN tb_role_permission.permission_id IS '权限ID';

-- ----------------------------
-- Table structure for tb_system_params
-- ----------------------------
DROP TABLE IF EXISTS tb_system_params;
CREATE TABLE tb_system_params (
    param_id VARCHAR(64) PRIMARY KEY NOT NULL,
    eeg_frequency FLOAT DEFAULT NULL,
    electrode_count INTEGER DEFAULT NULL,
    scale_question_num INTEGER DEFAULT NULL,
    model_num INTEGER DEFAULT NULL,
    id INTEGER NOT NULL
);
COMMENT ON TABLE tb_system_params IS '系统参数表';
COMMENT ON COLUMN tb_system_params.param_id IS '参数ID，主键';
COMMENT ON COLUMN tb_system_params.eeg_frequency IS '脑电数据采样频率 (Hz)';
COMMENT ON COLUMN tb_system_params.electrode_count IS '电极数量';
COMMENT ON COLUMN tb_system_params.scale_question_num IS '量表问题数量';
COMMENT ON COLUMN tb_system_params.model_num IS '系统中可用的模型数量';
COMMENT ON COLUMN tb_system_params.id IS 'ID';

-- ----------------------------
-- Records of tb_system_params
-- ----------------------------
INSERT INTO tb_system_params (param_id, eeg_frequency, electrode_count, scale_question_num, model_num, id) VALUES 
('PARAM_001', 500, 64, 40, 3, 1);
