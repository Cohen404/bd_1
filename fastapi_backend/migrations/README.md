# 数据库迁移脚本

本目录包含所有数据库迁移脚本，用于更新和修改数据库结构。

## 迁移脚本列表

| 序号 | 脚本文件 | 说明 |
|------|----------|------|
| 1 | add_has_result_field.py | 添加 `has_result` 字段到 `tb_data` 表 |
| 2 | add_result_fields.py | 添加 `personnel_id`, `personnel_name`, `active_learned` 字段到 `tb_result` 表 |
| 3 | update_result_personnel_info.py | 更新已有结果记录的人员信息 |
| 4 | add_data_active_learned_field.py | 添加 `active_learned` 字段到 `tb_data` 表 |
| 5 | add_result_overall_risk_level.py | 添加 `overall_risk_level` 字段到 `tb_result` 表 |
| 6 | update_result_overall_risk_level.py | 更新已有结果记录的总体风险等级 |
| 7 | add_blood_oxygen_pressure.py | 添加 `blood_oxygen`, `blood_pressure` 字段到 `tb_result` 表 |
| 8 | remove_social_isolation_score.py | 删除 `social_isolation_score` 字段 |
| 9 | add_md5_fields.py | 添加 `md5` 字段到 `tb_data`/`tb_result` 表 |

## 一键执行所有迁移

### 使用方法

在 `fastapi_backend` 目录下运行以下命令：

```bash
conda activate bd
python -m migrations.run_all_migrations
```

### 执行说明

- 脚本会按照正确的顺序依次执行所有迁移
- 如果某个字段已经存在，会自动跳过并显示警告
- 所有迁移执行完成后会显示执行结果统计
- 如果某个迁移失败，会显示详细的错误信息

### 执行输出示例

```
============================================================
开始执行所有数据库迁移
============================================================

============================================================
执行迁移: 添加 has_result 字段到 tb_data 表
模块: add_has_result_field
============================================================
成功添加 has_result 字段到 tb_data 表
✓ 迁移成功: 添加 has_result 字段到 tb_data 表

============================================================
执行迁移: 添加 personnel_id, personnel_name, active_learned 字段到 tb_result 表
模块: add_result_fields
============================================================
成功添加字段到 tb_result 表
✓ 迁移成功: 添加 personnel_id, personnel_name, active_learned 字段到 tb_result 表

... (其他迁移)

============================================================
迁移执行完成
============================================================
总计: 6 个迁移
成功: 6 个
失败: 0 个

✓ 所有迁移执行成功！
```

## 单独执行某个迁移

如果只需要执行某个特定的迁移，可以单独运行对应的脚本：

```bash
# 示例：只添加 has_result 字段
python -m migrations.add_has_result_field

# 示例：只更新总体风险等级
python -m migrations.update_result_overall_risk_level
```

## 注意事项

1. **执行顺序**：请按照脚本列表中的顺序执行迁移，确保依赖关系正确
2. **重复执行**：脚本支持重复执行，已存在的字段会自动跳过
3. **数据库备份**：在执行迁移前，建议先备份数据库
4. **错误处理**：如果某个迁移失败，请检查错误信息并修复问题后重新运行

## 迁移详情

### 1. add_has_result_field.py
- **表**: `tb_data`
- **新增字段**: `has_result` (BOOLEAN, 默认 FALSE)
- **说明**: 标记数据是否有评估结果

### 2. add_result_fields.py
- **表**: `tb_result`
- **新增字段**:
  - `personnel_id` (VARCHAR(64))
  - `personnel_name` (VARCHAR(255))
  - `active_learned` (BOOLEAN, 默认 FALSE)
- **说明**: 添加人员信息和主动学习状态字段

### 3. update_result_personnel_info.py
- **表**: `tb_result`
- **操作**: 更新已有记录的人员信息
- **说明**: 从 `tb_data` 表同步人员信息到 `tb_result` 表

### 4. add_data_active_learned_field.py
- **表**: `tb_data`
- **新增字段**: `active_learned` (BOOLEAN, 默认 FALSE)
- **说明**: 标记数据是否进行过主动学习

### 5. add_result_overall_risk_level.py
- **表**: `tb_result`
- **新增字段**: `overall_risk_level` (VARCHAR(20), 默认 '低风险')
- **说明**: 存储总体风险等级（低风险/高风险）

### 6. update_result_overall_risk_level.py
- **表**: `tb_result`
- **操作**: 更新已有记录的总体风险等级
- **说明**: 根据三个评估分数的平均值计算总体风险等级
  - 平均分 ≥ 50: 高风险
  - 平均分 < 50: 低风险

### 7. add_blood_oxygen_pressure.py
- **表**: `tb_result`
- **新增字段**:
  - `blood_oxygen` (FLOAT)
  - `blood_pressure` (VARCHAR(20))
- **说明**: 添加血氧和血压字段

### 8. remove_social_isolation_score.py
- **表**: `tb_result`
- **操作**: 删除 `social_isolation_score` 字段

### 9. add_md5_fields.py
- **表**: `tb_data`, `tb_result`
- **新增字段**: `md5` (VARCHAR(32))
- **说明**: 存储上传文件的MD5

## 故障排除

### 问题：字段已存在错误
**解决方案**: 脚本会自动检测并跳过已存在的字段，可以安全地重复运行

### 问题：连接数据库失败
**解决方案**: 检查数据库配置文件 `database.py` 中的连接信息是否正确

### 问题：权限不足
**解决方案**: 确保数据库用户有足够的权限执行 ALTER TABLE 和 UPDATE 操作


tb_data columns:
- id (integer)
- personnel_id (character varying)
- data_path (character varying)
- upload_user (integer)
- personnel_name (character varying)
- user_id (character varying)
- upload_time (timestamp without time zone)
- processing_status (character varying)
- feature_status (character varying)
- has_result (boolean)
- active_learned (boolean)
- md5 (character varying)

tb_result columns:
- id (integer)
- result_time (timestamp without time zone)
- stress_score (double precision)
- depression_score (double precision)
- anxiety_score (double precision)
- report_path (character varying)
- user_id (character varying)
- data_id (integer)
- personnel_id (character varying)
- personnel_name (character varying)
- active_learned (boolean)
- overall_risk_level (character varying)
- blood_oxygen (double precision)
- blood_pressure (character varying)
- md5 (character varying)