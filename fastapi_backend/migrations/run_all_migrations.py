"""
一键执行所有数据库迁移脚本
执行顺序：
1. add_has_result_field.py - 添加 has_result 字段到 tb_data 表
2. add_result_fields.py - 添加 personnel_id, personnel_name, active_learned 字段到 tb_result 表
3. update_result_personnel_info.py - 更新已有结果记录的人员信息
4. add_data_active_learned_field.py - 添加 active_learned 字段到 tb_data 表
5. add_result_overall_risk_level.py - 添加 overall_risk_level 字段到 tb_result 表
6. update_result_overall_risk_level.py - 更新已有结果记录的总体风险等级
7. add_blood_oxygen_pressure.py - 添加 blood_oxygen, blood_pressure 字段到 tb_result 表
8. remove_social_isolation_score.py - 删除 social_isolation_score 字段
9. add_md5_fields.py - 添加 md5 字段到 tb_data/tb_result 表
10. init_parameters_defaults.py - 初始化系统参数的默认值

运行方式: python -m migrations.run_all_migrations
"""

import sys
import importlib
from pathlib import Path

# 定义迁移脚本列表（按执行顺序）
MIGRATIONS = [
    ("添加 has_result 字段到 tb_data 表", "add_has_result_field"),
    ("添加 personnel_id, personnel_name, active_learned 字段到 tb_result 表", "add_result_fields"),
    ("更新已有结果记录的人员信息", "update_result_personnel_info"),
    ("添加 active_learned 字段到 tb_data 表", "add_data_active_learned_field"),
    ("添加 overall_risk_level 字段到 tb_result 表", "add_result_overall_risk_level"),
    ("更新已有结果记录的总体风险等级", "update_result_overall_risk_level"),
    ("添加 blood_oxygen, blood_pressure 字段到 tb_result 表", "add_blood_oxygen_pressure"),
    ("删除 social_isolation_score 字段", "remove_social_isolation_score"),
    ("添加 md5 字段到 tb_data/tb_result 表", "add_md5_fields"),
    ("初始化系统参数的默认值", "init_parameters_defaults"),
]

def run_migration(description: str, module_name: str) -> bool:
    """
    执行单个迁移脚本
    
    Args:
        description: 迁移描述
        module_name: 模块名称
        
    Returns:
        bool: 是否成功
    """
    print(f"\n{'='*60}")
    print(f"执行迁移: {description}")
    print(f"模块: {module_name}")
    print(f"{'='*60}")
    
    try:
        # 动态导入模块
        module = importlib.import_module(f"migrations.{module_name}")
        
        # 查找主函数
        main_func = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                # 排除类和特殊方法
                if attr_name not in ['text', 'SessionLocal', 'engine', 'Base', 'importlib', 'sys', 'Path']:
                    main_func = attr
                    break
        
        if main_func is None:
            print(f"错误: 在模块 {module_name} 中未找到主函数")
            return False
        
        # 执行主函数
        main_func()
        print(f"✓ 迁移成功: {description}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        # 检查是否是字段已存在的错误
        if 'DuplicateColumn' in error_msg or '已经存在' in error_msg or '已存在' in error_msg:
            print(f"⚠ 字段已存在，跳过: {description}")
            print(f"提示: 这通常表示该迁移之前已经执行过了")
            return True
        else:
            print(f"✗ 迁移失败: {description}")
            print(f"错误信息: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def run_all_migrations():
    """
    执行所有迁移脚本
    """
    print("\n" + "="*60)
    print("开始执行所有数据库迁移")
    print("="*60)
    
    success_count = 0
    failed_count = 0
    failed_migrations = []
    
    for description, module_name in MIGRATIONS:
        if run_migration(description, module_name):
            success_count += 1
        else:
            failed_count += 1
            failed_migrations.append((description, module_name))
    
    # 打印总结
    print("\n" + "="*60)
    print("迁移执行完成")
    print("="*60)
    print(f"总计: {len(MIGRATIONS)} 个迁移")
    print(f"成功: {success_count} 个")
    print(f"失败: {failed_count} 个")
    
    if failed_migrations:
        print("\n失败的迁移:")
        for description, module_name in failed_migrations:
            print(f"  - {description} ({module_name})")
        print("\n请检查错误信息并修复问题后重新运行")
        return False
    else:
        print("\n✓ 所有迁移执行成功！")
        return True

if __name__ == "__main__":
    success = run_all_migrations()
    sys.exit(0 if success else 1)
