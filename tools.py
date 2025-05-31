import os
import re

def remove_newline_from_title(directory):
    """
    遍历指定目录下的所有 MDX 文件，并去除文件内 'title' 字段中的换行符。

    Args:
        directory (str): 包含 MDX 文件的目录路径。
    """
    for filename in os.listdir(directory):
        if filename.endswith(".mdx"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                modified_lines = []
                in_title_section = False
                for i, line in enumerate(lines):
                    if line.strip().startswith("title:"):
                        in_title_section = True
                        # 检查title是否跨行
                        if i + 1 < len(lines) and not re.match(r'^\s*[\w\-\_]+\s*:\s*".*?"\s*$', lines[i+1]):
                            # 如果下一行不是另一个key-value对，则认为是title的跨行部分
                            combined_title_line = line.strip()
                            j = i + 1
                            while j < len(lines) and not re.match(r'^\s*[\w\-\_]+\s*:\s*".*?"\s*$', lines[j]) and lines[j].strip() != "":
                                combined_title_line += " " + lines[j].strip()
                                j += 1
                            modified_lines.append(combined_title_line + "\n")
                            # 跳过已经被合并的行
                            for _ in range(i + 1, j):
                                lines[_] = "" # 将合并的行标记为空，后续不再处理
                            in_title_section = False # 结束title处理
                        else:
                            modified_lines.append(line)
                            in_title_section = False # 如果是单行title，直接添加并结束
                    elif in_title_section and line.strip() != "":
                        # 如果在title部分，且当前行不是空行，则将其视为title的延续，并去除换行符
                        modified_lines[-1] = modified_lines[-1].strip() + " " + line.strip() + "\n"
                    else:
                        modified_lines.append(line)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(modified_lines)
                print(f"Processed: {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

# 请将 'your_directory_path_here' 替换为你的 MDX 文件所在的实际目录路径
directory_to_process = './blog'
remove_newline_from_title(directory_to_process)