import os
import glob
import shutil
from pathlib import Path
import argparse

def restore_backup_srt_files(directory_path, recursive=False):
    """
    删除生成的.en.srt和.zh.srt文件，并将.srt.bak文件恢复为原始的.srt文件
    
    参数:
        directory_path: 要处理的目录路径
        recursive: 是否递归处理子目录
    """
    # 使用Path对象处理路径
    directory = Path(directory_path)
    
    # 检查目录是否存在
    if not directory.exists() or not directory.is_dir():
        print(f"错误: 目录 '{directory}' 不存在或不是一个目录")
        return
    
    # 定义搜索模式
    pattern = "**/*.srt*" if recursive else "*.srt*"
    
    # 收集所有需要删除的.en.srt和.zh.srt文件
    en_zh_files = []
    # 收集所有需要恢复的.srt.bak文件
    bak_files = []
    
    # 搜索文件
    for file_path in directory.glob(pattern):
        if file_path.is_file():
            file_str = str(file_path)
            if file_str.endswith('.en.srt') or file_str.endswith('.zh.srt'):
                en_zh_files.append(file_path)
            elif file_str.endswith('.srt.bak'):
                bak_files.append(file_path)
    
    # 删除.en.srt和.zh.srt文件
    deleted_count = 0
    for file_path in en_zh_files:
        try:
            os.remove(file_path)
            print(f"已删除: {file_path}")
            deleted_count += 1
        except Exception as e:
            print(f"删除文件 '{file_path}' 时出错: {str(e)}")
    
    # 恢复.srt.bak文件
    restored_count = 0
    for bak_path in bak_files:
        try:
            # 计算原始文件路径 (.srt.bak -> .srt)
            original_path = str(bak_path)[:-4]  # 移除 '.bak'
            
            # 恢复备份
            shutil.copy2(bak_path, original_path)
            print(f"已恢复: {bak_path} -> {original_path}")
            
            # 删除备份文件
            os.remove(bak_path)
            print(f"已删除备份: {bak_path}")
            
            restored_count += 1
        except Exception as e:
            print(f"恢复文件 '{bak_path}' 时出错: {str(e)}")
    
    print(f"\n处理完成! 已删除 {deleted_count} 个分割字幕文件，恢复了 {restored_count} 个原始字幕文件。")

def main():
    # 使用argparse处理命令行参数
    parser = argparse.ArgumentParser(description='删除生成的.en.srt和.zh.srt文件，并将.srt.bak文件恢复为原始的.srt文件')
    parser.add_argument('directory', help='要处理的目录路径')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    
    args = parser.parse_args()
    
    directory_path = args.directory
    recursive = args.recursive
    
    # 如果路径包含引号，去除它们
    if directory_path.startswith('"') and directory_path.endswith('"'):
        directory_path = directory_path[1:-1]
    
    print(f"处理目录: {directory_path}" + (" (包含子目录)" if recursive else " (不包含子目录)"))
    
    # 执行恢复操作
    restore_backup_srt_files(directory_path, recursive)

if __name__ == "__main__":
    main()
