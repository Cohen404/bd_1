import os

RECORDINGS_DIR = r'd:\programme\bd_1\eegs\Recordings'

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if len(lines) <= 100000:
        print(f"{os.path.basename(filepath)}: 文件行数({len(lines)}) <= 100000，跳过")
        return
    
    kept_lines = lines[99999:99999 + 10000]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(kept_lines)
    
    print(f"{os.path.basename(filepath)}: 已从 {len(lines)} 行减少到 10000 行（保留第100000-109999行）")

def main():
    txt_files = [f for f in os.listdir(RECORDINGS_DIR) if f.endswith('.txt')]
    
    print(f"找到 {len(txt_files)} 个TXT文件")
    
    for filename in txt_files:
        filepath = os.path.join(RECORDINGS_DIR, filename)
        process_file(filepath)
    
    print("处理完成！")

if __name__ == '__main__':
    main()
