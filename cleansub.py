import os
import sys
import argparse

def clean_subtitle(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    current_subtitle = []
    subtitle_number = None
    time_stamp = None
    
    for line in lines:
        line = line.strip()
        if not line:  # 空行
            if subtitle_number and time_stamp and current_subtitle:
                # 合并字幕文本，去除\h并确保空格正确
                subtitle_text = ' '.join(current_subtitle)
                subtitle_text = subtitle_text.replace('\\h', '').strip()
                # 确保单词之间有空格
                subtitle_text = subtitle_text.replace('  ', ' ')
                
                cleaned_lines.append(subtitle_number)
                cleaned_lines.append(time_stamp)
                cleaned_lines.append(subtitle_text)
                cleaned_lines.append('')  # 添加空行分隔
            
            subtitle_number = None
            time_stamp = None
            current_subtitle = []
            continue
        
        if subtitle_number is None:
            subtitle_number = line
        elif time_stamp is None:
            time_stamp = line
        else:
            current_subtitle.append(line)
    
    # 处理最后一个字幕
    if subtitle_number and time_stamp and current_subtitle:
        subtitle_text = ' '.join(current_subtitle)
        subtitle_text = subtitle_text.replace('\\h', '').strip()
        subtitle_text = subtitle_text.replace('  ', ' ')
        
        cleaned_lines.append(subtitle_number)
        cleaned_lines.append(time_stamp)
        cleaned_lines.append(subtitle_text)
    
    # 写入输出文件（覆盖原文件）
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print(f"已清理并覆盖保存: {input_file}")

def process_folder(folder_path, include_subfolders=False):
    # 确保路径存在
    if not os.path.exists(folder_path):
        print(f"错误: 路径 '{folder_path}' 不存在")
        return
    
    srt_files = []
    
    if include_subfolders:
        # 递归遍历所有子文件夹
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.srt'):
                    srt_files.append(os.path.join(root, file))
    else:
        # 只处理指定文件夹
        for file in os.listdir(folder_path):
            if file.lower().endswith('.srt'):
                srt_files.append(os.path.join(folder_path, file))
    
    if not srt_files:
        if include_subfolders:
            print(f"在 '{folder_path}' 及其子文件夹中没有找到 .srt 文件")
        else:
            print(f"在 '{folder_path}' 文件夹中没有找到 .srt 文件")
    else:
        print(f"找到 {len(srt_files)} 个 .srt 文件，开始处理...")
        for srt_file in srt_files:
            clean_subtitle(srt_file)
        print("所有字幕文件处理完成")

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='清理字幕文件，合并多行文本并去除特殊标记')
    parser.add_argument('folder', nargs='?', default='.', 
                       help='要处理的文件夹路径 (默认为当前文件夹)')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='递归处理子文件夹中的字幕文件')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 处理指定文件夹
    process_folder(args.folder, args.recursive)

if __name__ == "__main__":
    main()

