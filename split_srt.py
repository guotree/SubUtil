import re
import os
import sys
import glob
import shutil
from pathlib import Path
import unicodedata
import argparse

def is_chinese(text):
    """
    判断文本是否为中文
    """
    # 如果包含中文字符，则认为是中文文本
    for char in text:
        if 'CJK' in unicodedata.name(char, ''):
            return True
    return False

def detect_language(text):
    """
    检测文本是英文还是中文
    返回: 'en' 表示英文, 'zh' 表示中文
    """
    # 计算中文字符的比例
    chinese_chars = sum(1 for char in text if 'CJK' in unicodedata.name(char, ''))
    total_chars = len(text.strip())
    
    # 如果中文字符比例超过20%，则认为是中文
    if total_chars > 0 and chinese_chars / total_chars > 0.2:
        return 'zh'
    else:
        return 'en'

def split_bilingual_srt(srt_file_path):
    """
    将双语SRT字幕文件分割为单独的中文和英文字幕文件，备份原始文件并删除原始文件
    
    参数:
        srt_file_path: 原始SRT文件的路径
    """
    # 检查文件是否存在
    if not os.path.exists(srt_file_path):
        print(f"错误: 文件 '{srt_file_path}' 不存在")
        return False
    
    try:
        # 准备输出文件名
        file_path = Path(srt_file_path)
        file_stem = file_path.stem  # 获取不带扩展名的文件名
        file_ext = file_path.suffix  # 获取扩展名
        
        en_output_path = str(file_path.with_name(f"{file_stem}.en{file_ext}"))
        zh_output_path = str(file_path.with_name(f"{file_stem}.zh{file_ext}"))
        backup_path = str(file_path.with_name(f"{file_stem}{file_ext}.bak"))
        
        # 读取原始SRT文件
        content = None
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'utf-16']
        
        for encoding in encodings:
            try:
                with open(srt_file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"成功使用 {encoding} 编码读取文件")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"错误: 无法解码文件 '{srt_file_path}'，尝试了以下编码: {encodings}")
            return False
        
        # 使用正则表达式分割字幕块
        subtitle_blocks = re.split(r'\n\s*\n', content.strip())
        
        en_subtitles = []
        zh_subtitles = []
        
        for block in subtitle_blocks:
            lines = block.strip().split('\n')
            
            if len(lines) < 3:
                # 跳过格式不正确的块
                continue
            
            # 第一行是序号，第二行是时间码
            subtitle_number = lines[0]
            time_code = lines[1]
            
            # 文本内容从第三行开始
            text_lines = lines[2:]
            
            # 如果只有一行文本，复制到两个字幕文件中
            if len(text_lines) == 1:
                en_subtitles.append(f"{subtitle_number}\n{time_code}\n{text_lines[0]}\n")
                zh_subtitles.append(f"{subtitle_number}\n{time_code}\n{text_lines[0]}\n")
                continue
            
            # 检测每行文本的语言
            line_languages = [detect_language(line) for line in text_lines]
            
            # 分离英文和中文文本
            en_text_lines = []
            zh_text_lines = []
            
            for i, line in enumerate(text_lines):
                if line_languages[i] == 'en':
                    en_text_lines.append(line)
                else:
                    zh_text_lines.append(line)
            
            # 如果没有检测到某种语言，使用另一种语言的文本
            if not en_text_lines:
                en_text_lines = zh_text_lines
            if not zh_text_lines:
                zh_text_lines = en_text_lines
            
            # 添加到英文字幕列表
            en_text = '\n'.join(en_text_lines)
            en_subtitles.append(f"{subtitle_number}\n{time_code}\n{en_text}\n")
            
            # 添加到中文字幕列表
            zh_text = '\n'.join(zh_text_lines)
            zh_subtitles.append(f"{subtitle_number}\n{time_code}\n{zh_text}\n")
        
        # 备份原始文件
        shutil.copy2(srt_file_path, backup_path)
        print(f"原始文件已备份到: {backup_path}")
        
        # 写入英文字幕文件
        with open(en_output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(en_subtitles))
        
        # 写入中文字幕文件
        with open(zh_output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(zh_subtitles))
        
        print(f"英文字幕已保存到: {en_output_path}")
        print(f"中文字幕已保存到: {zh_output_path}")
        
        # 删除原始文件
        os.remove(srt_file_path)
        print(f"原始文件已删除: {srt_file_path}")
        
        return True
        
    except Exception as e:
        print(f"处理文件 '{srt_file_path}' 时出错: {str(e)}")
        return False

def find_srt_files(directory_path, recursive=True):
    """
    查找目录中的所有SRT文件
    
    参数:
        directory_path: 要搜索的目录路径
        recursive: 是否递归搜索子目录
    
    返回:
        SRT文件路径列表
    """
    srt_files = []
    
    # 使用Path对象处理路径，更好地处理特殊字符
    directory = Path(directory_path)
    
    # 检查目录是否存在
    if not directory.exists() or not directory.is_dir():
        print(f"错误: 目录 '{directory}' 不存在或不是一个目录")
        return []
    
    # 定义要搜索的模式
    pattern = "**/*.srt" if recursive else "*.srt"
    
    # 查找所有SRT文件（不区分大小写）
    for file_path in directory.glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() == ".srt":
            # 排除已经处理过的.en.srt和.zh.srt文件以及备份文件
            if not (str(file_path).endswith('.en.srt') or 
                    str(file_path).endswith('.zh.srt') or 
                    str(file_path).endswith('.srt.bak')):
                srt_files.append(str(file_path))
    
    return srt_files

def process_directory(directory_path, recursive=True):
    """
    处理指定目录下的所有SRT文件
    
    参数:
        directory_path: 要处理的目录路径
        recursive: 是否递归处理子目录
    """
    print(f"搜索目录: {directory_path}")
    
    # 查找所有SRT文件
    srt_files = find_srt_files(directory_path, recursive)
    
    if not srt_files:
        print(f"在目录 '{directory_path}' 中没有找到需要处理的SRT文件")
        # 打印目录内容以帮助调试
        try:
            print("\n目录内容:")
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isdir(item_path):
                    print(f"  [目录] {item}")
                else:
                    print(f"  [文件] {item}")
        except Exception as e:
            print(f"无法列出目录内容: {str(e)}")
        return
    
    print(f"找到 {len(srt_files)} 个需要处理的SRT文件:")
    for file in srt_files:
        print(f"  - {file}")
    
    # 处理每个SRT文件
    success_count = 0
    for srt_file in srt_files:
        print(f"\n处理文件: {srt_file}")
        if split_bilingual_srt(srt_file):
            success_count += 1
        print("-" * 40)
    
    print(f"\n处理完成! 成功处理 {success_count}/{len(srt_files)} 个文件")

def main():
    # 使用argparse处理命令行参数
    parser = argparse.ArgumentParser(description='将双语SRT字幕文件分割为单独的中文和英文字幕文件')
    parser.add_argument('directory', help='要处理的目录路径')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    parser.add_argument('--debug', action='store_true', help='显示调试信息')
    
    args = parser.parse_args()
    
    directory_path = args.directory
    recursive = args.recursive
    
    # 如果路径包含引号，去除它们
    if directory_path.startswith('"') and directory_path.endswith('"'):
        directory_path = directory_path[1:-1]
    
    print(f"处理目录: {directory_path}" + (" (包含子目录)" if recursive else " (不包含子目录)"))
    
    # 检查路径是否存在
    if not os.path.exists(directory_path):
        print(f"错误: 目录 '{directory_path}' 不存在")
        return
    
    if args.debug:
        print("\n调试信息:")
        print(f"  当前工作目录: {os.getcwd()}")
        print(f"  目录是否存在: {os.path.exists(directory_path)}")
        print(f"  是否为目录: {os.path.isdir(directory_path)}")
        try:
            print(f"  目录内容: {os.listdir(directory_path)}")
        except Exception as e:
            print(f"  无法列出目录内容: {str(e)}")
    
    process_directory(directory_path, recursive)

if __name__ == "__main__":
    main()
