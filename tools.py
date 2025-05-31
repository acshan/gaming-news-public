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

def fix_mdx_syntax_errors(directory):
    """
    遍历指定目录下的所有 MDX 文件，修复常见的 MDX 语法错误：
    1. 修复文本和带HTML标签的Markdown链接之间缺少空格的问题
    2. 修复HTML标签在Markdown链接中的格式问题
    3. 修复其他可能导致 MDX 解析错误的格式问题

    Args:
        directory (str): 包含 MDX 文件的目录路径。
    """
    # 匹配没有空格的文本后跟着的Markdown链接（包含HTML标签）
    text_link_pattern = re.compile(r'(\w+)(\[<[\w\/]+>.*?</[\w\/]+>\]\(.*?\))')
    
    # 匹配没有空格的文本后跟着的普通Markdown链接
    text_normal_link_pattern = re.compile(r'(\w+)(\[(?!<).*?\]\(.*?\))')
    
    # 匹配HTML标签内不正确的空格位置
    html_tag_space_pattern = re.compile(r'<(\w+)> (.*?)</\1>')
    
    # 匹配未闭合的HTML标签
    unclosed_tag_pattern = re.compile(r'<(\w+)>(.*?)(?!</\1>)(\n|$)')
    
    # 匹配Markdown链接中的HTML标签，确保它们的格式正确
    # 这个模式特别处理像 [<u> text</u>](url) 这样的情况，确保<u>和</u>之间没有不必要的空格
    markdown_html_tag_pattern = re.compile(r'\[<(\w+)>\s+(.*?)</\1>\]\((.*?)\)')
    
    for filename in os.listdir(directory):
        if filename.endswith(".mdx"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 保存原始内容用于比较
                original_content = content
                
                # 修复文本和带HTML标签的链接之间缺少空格的问题
                content = text_link_pattern.sub(r'\1 \2', content)
                
                # 修复文本和普通链接之间缺少空格的问题
                content = text_normal_link_pattern.sub(r'\1 \2', content)
                
                # 修复HTML标签内的空格问题
                content = html_tag_space_pattern.sub(r'<\1>\2</\1>', content)
                
                # 修复Markdown链接中的HTML标签格式
                # 将 [<u> text</u>](url) 转换为 [<u>text</u>](url)
                content = markdown_html_tag_pattern.sub(r'[<\1>\2</\1>](\3)', content)
                
                # 检测未闭合的HTML标签（此处只是标记，不自动修复，因为自动修复可能导致语义变化）
                unclosed_tags = unclosed_tag_pattern.findall(content)
                if unclosed_tags:
                    print(f"Warning: Unclosed HTML tags found in {filename}:")
                    for tag, content_part, _ in unclosed_tags:
                        print(f"  - <{tag}>{content_part[:30]}... is missing closing tag")
                
                # 如果内容有变化，写回文件
                if original_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Fixed syntax in: {filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")

def validate_mdx_files(directory):
    """
    验证指定目录下的所有 MDX 文件，检查是否存在语法错误，但不修改文件。
    可以在生成 MDX 文件后运行此函数来验证文件是否有语法问题。

    Args:
        directory (str): 包含 MDX 文件的目录路径。
    
    Returns:
        list: 包含错误信息的列表，每个元素是 (filename, error_message) 元组。
    """
    errors = []
    
    # 可能导致MDX解析错误的模式
    problematic_patterns = [
        (r'\w+\[<\w+>', '文本和带HTML标签的链接之间缺少空格'),
        (r'\w+\[(?!<)[^\]]+\]', '文本和普通链接之间缺少空格'),
        (r'<(\w+)> (.*?)</\1>', 'HTML标签内有不必要的空格'),
        (r'<(\w+)>(.*?)(?!</\1>)(\n|$)', '未闭合的HTML标签'),
        (r'\[<(\w+)>\s+(.*?)</\1>\]\((.*?)\)', 'Markdown链接中HTML标签内有不必要的空格')
    ]
    
    for filename in os.listdir(directory):
        if filename.endswith(".mdx"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查各种可能的问题
                for pattern, error_desc in problematic_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_number = content[:match.start()].count('\n') + 1
                        context = content[max(0, match.start()-20):match.end()+20].replace('\n', ' ')
                        errors.append((filename, f"行 {line_number}: {error_desc} - 上下文: ...{context}..."))
                
            except Exception as e:
                errors.append((filename, f"处理文件时出错: {e}"))
    
    return errors

if __name__ == "__main__":
    directory_to_process = './blog'
    
    # 先验证文件，输出可能的问题
    print("验证 MDX 文件...")
    errors = validate_mdx_files(directory_to_process)
    if errors:
        print(f"发现 {len(errors)} 个潜在问题:")
        for filename, error in errors:
            print(f"{filename}: {error}")
        
        # 询问是否要自动修复
        print("\n是否要尝试自动修复这些问题? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            remove_newline_from_title(directory_to_process)
            fix_mdx_syntax_errors(directory_to_process)
            print("修复完成。")
        else:
            print("未进行修复。")
    else:
        print("未发现问题。")
        
    # 如果直接想修复而不验证，可以取消下面两行的注释
    # remove_newline_from_title(directory_to_process)
    # fix_mdx_syntax_errors(directory_to_process)