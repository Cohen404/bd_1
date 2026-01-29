#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按照修改时间从早到晚重命名images目录中的图片
"""

import os
import glob
from pathlib import Path

def rename_images_by_mtime(directory):
    """
    按照修改时间从早到晚重命名图片
    
    参数:
        directory: 图片目录路径
    """
    # 获取所有jpg文件
    image_files = glob.glob(os.path.join(directory, '*.jpg'))
    
    if not image_files:
        print(f"在 {directory} 目录下没有找到jpg文件")
        return
    
    # 按修改时间排序（从早到晚）
    image_files.sort(key=lambda x: os.path.getmtime(x))
    
    print(f"找到 {len(image_files)} 个jpg文件")
    print("=" * 60)
    print("按修改时间排序（从早到晚）：")
    print("=" * 60)
    
    # 显示排序结果
    for idx, img_path in enumerate(image_files, 1):
        mtime = os.path.getmtime(img_path)
        from datetime import datetime
        mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{idx:2d}. {os.path.basename(img_path):20s} - {mtime_str}")
    
    print("=" * 60)
    
    # 创建临时文件名，避免覆盖
    temp_files = []
    for idx, img_path in enumerate(image_files, 1):
        temp_name = os.path.join(directory, f"temp_{idx}.jpg")
        temp_files.append((img_path, temp_name))
    
    # 第一步：重命名为临时文件名
    print("\n第一步：重命名为临时文件...")
    for old_path, temp_path in temp_files:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        os.rename(old_path, temp_path)
        print(f"  {os.path.basename(old_path)} -> temp_{os.path.basename(temp_path).split('_')[1]}")
    
    # 第二步：重命名为最终文件名
    print("\n第二步：重命名为最终文件名...")
    for idx, (old_path, temp_path) in enumerate(temp_files, 1):
        final_name = os.path.join(directory, f"{idx}.jpg")
        if os.path.exists(final_name):
            os.remove(final_name)
        os.rename(temp_path, final_name)
        print(f"  temp_{idx}.jpg -> {idx}.jpg")
    
    print("=" * 60)
    print(f"完成！已将 {len(image_files)} 个文件按修改时间重命名为 1.jpg 到 {len(image_files)}.jpg")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='按照修改时间从早到晚重命名图片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 重命名images目录中的图片
  python rename_images.py -d images/
  
  # 使用默认目录
  python rename_images.py
        """
    )
    
    parser.add_argument('-d', '--directory', help='图片目录路径')
    
    args = parser.parse_args()
    
    # 确定目录
    if args.directory:
        if not os.path.isdir(args.directory):
            print(f"错误: 目录不存在 {args.directory}")
            return
        target_dir = args.directory
    else:
        # 默认使用fastapi_backend/images目录
        target_dir = os.path.join(os.path.dirname(__file__), 'images')
        if not os.path.isdir(target_dir):
            print(f"错误: 默认目录不存在 {target_dir}")
            parser.print_help()
            return
    
    print(f"目标目录: {target_dir}\n")
    rename_images_by_mtime(target_dir)

if __name__ == '__main__':
    main()
