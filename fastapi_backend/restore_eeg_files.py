import os
import shutil

SOURCE_DIR = r'D:\Users\JD\Desktop\Recordings'
TARGET_DIR = r'd:\programme\bd_1\eegs\Recordings'

files_to_restore = [
    'OpenBCI-RAW-2025-12-13_17-41-18.txt',
    'OpenBCI-RAW-2025-12-13_17-52-56.txt',
    'OpenBCI-RAW-2025-12-13_18-04-01.txt',
    'OpenBCI-RAW-2025-12-13_19-42-48.txt',
    'OpenBCI-RAW-2025-12-13_19-54-42.txt',
    'OpenBCI-RAW-2025-12-13_20-05-31.txt',
    'OpenBCI-RAW-2025-12-13_20-11-10.txt',
    'OpenBCI-RAW-2025-12-14_10-50-26.txt',
    'OpenBCI-RAW-2025-12-14_11-00-34.txt',
    'OpenBCI-RAW-2025-12-14_20-11-44.txt',
    'OpenBCI-RAW-2025-12-14_20-22-55.txt',
    'OpenBCI-RAW-2025-12-14_20-36-35.txt',
    'OpenBCI-RAW-2025-12-14_21-08-58.txt',
    'OpenBCI-RAW-2025-12-15_08-38-15.txt',
    'OpenBCI-RAW-2025-12-15_09-19-35.txt',
    'OpenBCI-RAW-2025-12-15_12-25-19.txt',
    'OpenBCI-RAW-2025-12-15_12-35-01.txt',
    'OpenBCI-RAW-2025-12-15_12-44-13.txt',
    'OpenBCI-RAW-2025-12-15_12-50-57.txt',
    'OpenBCI-RAW-2025-12-15_12-57-06.txt',
    'OpenBCI-RAW-2025-12-15_14-10-20.txt',
    'OpenBCI-RAW-2025-12-15_14-22-30.txt',
    'OpenBCI-RAW-2025-12-15_14-33-32.txt',
    'OpenBCI-RAW-2025-12-15_14-40-17.txt',
    'OpenBCI-RAW-2025-12-15_20-44-51.txt',
    'OpenBCI-RAW-2025-12-15_20-51-32.txt'
]

def find_file_in_source(filename):
    for root, dirs, files in os.walk(SOURCE_DIR):
        if filename in files:
            return os.path.join(root, filename)
    return None

def main():
    restored_count = 0
    not_found_count = 0
    
    for filename in files_to_restore:
        source_path = find_file_in_source(filename)
        target_path = os.path.join(TARGET_DIR, filename)
        
        if source_path:
            try:
                shutil.copy2(source_path, target_path)
                restored_count += 1
                print(f"✓ 已还原: {filename}")
            except Exception as e:
                print(f"✗ 还原失败: {filename} - {str(e)}")
        else:
            not_found_count += 1
            print(f"✗ 未找到: {filename}")
    
    print(f"\n还原完成！")
    print(f"成功还原: {restored_count} 个文件")
    print(f"未找到: {not_found_count} 个文件")

if __name__ == '__main__':
    main()
