#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
format_gongwen.py - 公文格式化整合工具

一站式将 Word 或 Markdown 文件转换为符合公文规范的格式。

功能：
1. Word → 公文 TXT（一站式，去除 Markdown 符号）
2. Markdown → 公文 TXT
3. Word → 公文规范 Markdown（保留 Markdown 格式，仅转换引号）
4. 自动转换引号（半角 → 全角）

用法：
    python3 format_gongwen.py <input_file> [-o output_file] [-m/--markdown]

示例：
    python3 format_gongwen.py 报告.docx              # 输出到 报告.txt
    python3 format_gongwen.py 报告.md -o 最终版.txt  # 指定输出文件
    python3 format_gongwen.py 报告.docx -m           # 输出到 报告.md（保留 Markdown 格式）
"""

import sys
import re
import argparse
import tempfile
import subprocess
import shutil
from pathlib import Path


def remove_markdown_symbols(content: str) -> str:
    """
    去除 Markdown 格式符号，保留纯文本
    """
    lines = content.split("\n")
    cleaned_lines = []

    for line in lines:
        # 去除标题符号 # ## ### 等
        line = re.sub(r"^#{1,6}\s+", "", line)

        # 去除加粗符号 **text** 或 __text__
        line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        line = re.sub(r"__([^_]+)__", r"\1", line)

        # 去除斜体符号 *text* 或 _text_（注意不要误删下划线）
        line = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", line)

        # 去除行内代码符号 `text`
        line = re.sub(r"`([^`]+)`", r"\1", line)

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def merge_subtitles(content: str) -> str:
    """
    将独立的小标题融入下一段

    规则：
    - 如果一行是小标题（以（一）、（二）等开头），且下一行是空行
    - 则删除空行，将小标题与后续内容合并
    """
    lines = content.split("\n")
    result = []
    i = 0

    # 匹配二级标题模式：（一）、（二）等
    subtitle_pattern = re.compile(r"^（[一二三四五六七八九十]+）")

    while i < len(lines):
        current_line = lines[i].strip()

        # 检查是否是二级小标题行
        if subtitle_pattern.match(current_line):
            # 查找下一个非空行
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1

            if j < len(lines):
                # 将小标题与下一段内容合并
                next_content = lines[j].strip()
                # 如果小标题以句号结尾，直接拼接；否则加空格
                if current_line.endswith("。"):
                    merged = current_line + next_content
                else:
                    merged = current_line + next_content
                result.append(merged)
                i = j + 1
                continue

        result.append(lines[i])
        i += 1

    # 清理多余空行（3个以上变成2个）
    content = "\n".join(result)
    content = re.sub(r"\n{3,}", "\n\n", content)

    return content


def convert_quotes(text: str) -> str:
    """
    将半角双引号转换为全角双引号
    """
    HALF_QUOTE = chr(0x0022)  # " 半角双引号
    FULL_OPEN = chr(0x201C)  # " 全角左双引号
    FULL_CLOSE = chr(0x201D)  # " 全角右双引号

    result = []
    is_open = True

    for char in text:
        if ord(char) == 0x0022:
            if is_open:
                result.append(FULL_OPEN)
            else:
                result.append(FULL_CLOSE)
            is_open = not is_open
        else:
            result.append(char)

    return "".join(result)


def convert_word_to_md(input_path: Path, output_dir: Path) -> Path:
    """
    将 Word 文件转换为 Markdown
    """
    output_md = output_dir / (input_path.stem + ".md")

    # 查找 word2md.py 脚本
    script_locations = [
        Path(__file__).parent / "word2md.py",
        Path("word2md.py"),
        Path(__file__).parent.parent / "word2md.py",
    ]

    word2md_script = None
    for loc in script_locations:
        if loc.exists():
            word2md_script = loc
            break

    if word2md_script is None:
        print("错误：找不到 word2md.py 脚本")
        sys.exit(1)

    result = subprocess.run(
        ["python3", str(word2md_script), str(input_path), "-o", str(output_dir)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Word 转换失败: {result.stderr}")
        sys.exit(1)

    return output_md


def clean_md_file(md_path: Path) -> None:
    """
    清理 Markdown 文件中的遗留标记
    """
    script_locations = [
        Path(__file__).parent / "clean_md.py",
        Path("clean_md.py"),
        Path(__file__).parent.parent / "clean_md.py",
    ]

    clean_script = None
    for loc in script_locations:
        if loc.exists():
            clean_script = loc
            break

    if clean_script:
        subprocess.run(
            ["python3", str(clean_script), str(md_path), "-i"],
            capture_output=True,
            text=True,
        )


def convert_grid_tables(md_path: Path) -> None:
    """
    将 Grid Table 转换为 GFM Table
    """
    script_locations = [
        Path(__file__).parent / "grid2gfm.py",
        Path("grid2gfm.py"),
        Path(__file__).parent.parent / "grid2gfm.py",
    ]

    grid_script = None
    for loc in script_locations:
        if loc.exists():
            grid_script = loc
            break

    if grid_script:
        subprocess.run(
            ["python3", str(grid_script), str(md_path), "-i"],
            capture_output=True,
            text=True,
        )


def format_gongwen_txt(input_path: Path, output_path: Path) -> bool:
    """
    将输入文件转换为公文格式 TXT（去除 Markdown 符号）
    """
    suffix = input_path.suffix.lower()

    # 如果是 Word 文件，先转换为 Markdown
    if suffix in [".doc", ".docx"]:
        print(f"正在转换 Word 文件: {input_path.name}")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            md_path = convert_word_to_md(input_path, temp_path)
            clean_md_file(md_path)
            content = md_path.read_text(encoding="utf-8")
    elif suffix in [".md", ".txt"]:
        print(f"正在处理文件: {input_path.name}")
        content = input_path.read_text(encoding="utf-8")
    else:
        print(f"不支持的文件格式: {suffix}")
        return False

    # 步骤 1: 去除 Markdown 格式符号
    print("  - 去除 Markdown 格式符号...")
    content = remove_markdown_symbols(content)

    # 步骤 2: 融合小标题到段落
    print("  - 融合小标题到段落...")
    content = merge_subtitles(content)

    # 步骤 3: 转换引号
    print("  - 转换引号（半角 → 全角）...")
    half_quote_count = content.count(chr(0x0022))
    content = convert_quotes(content)

    if half_quote_count > 0:
        print(f"    转换了 {half_quote_count // 2} 对引号")
        if half_quote_count % 2 != 0:
            print("    警告：引号数量为奇数，可能存在未配对的引号")

    # 步骤 4: 最终清理
    content = content.rstrip("\n") + "\n"

    # 写入输出文件
    output_path.write_text(content, encoding="utf-8")
    print(f"完成: {output_path}")

    return True


def format_gongwen_markdown(input_path: Path, output_path: Path) -> bool:
    """
    将输入文件转换为公文规范 Markdown（保留 Markdown 格式，仅转换引号和清理遗留标记）
    """
    suffix = input_path.suffix.lower()

    # 如果是 Word 文件，先转换为 Markdown
    if suffix in [".doc", ".docx"]:
        print(f"正在转换 Word 文件: {input_path.name}")

        # 使用输出目录作为临时目录
        output_dir = output_path.parent
        md_path = convert_word_to_md(input_path, output_dir)

        # 清理遗留标记
        print("  - 清理 Word 转换遗留标记...")
        clean_md_file(md_path)

        # 转换表格格式
        print("  - 优化表格格式...")
        convert_grid_tables(md_path)

        # 读取清理后的内容
        content = md_path.read_text(encoding="utf-8")

        # 如果输出路径与临时 md 路径不同，需要移动或复制
        if md_path != output_path:
            # 删除临时文件（稍后写入正确路径）
            if md_path.exists() and md_path != output_path:
                pass  # 保留，后面会覆盖
    elif suffix in [".md", ".txt"]:
        print(f"正在处理文件: {input_path.name}")
        content = input_path.read_text(encoding="utf-8")
    else:
        print(f"不支持的文件格式: {suffix}")
        return False

    # 仅转换引号（保留 Markdown 格式）
    print("  - 转换引号（半角 → 全角）...")
    half_quote_count = content.count(chr(0x0022))
    content = convert_quotes(content)

    if half_quote_count > 0:
        print(f"    转换了 {half_quote_count // 2} 对引号")
        if half_quote_count % 2 != 0:
            print("    警告：引号数量为奇数，可能存在未配对的引号")

    # 最终清理
    content = content.rstrip("\n") + "\n"

    # 写入输出文件
    output_path.write_text(content, encoding="utf-8")
    print(f"完成: {output_path}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="公文格式化工具 - 将 Word/Markdown 转换为符合公文规范的格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 format_gongwen.py 报告.docx              # 输出到 报告.txt
  python3 format_gongwen.py 报告.md -o 最终版.txt  # 指定输出文件
  python3 format_gongwen.py 报告.docx -m           # 输出到 报告.md（保留 Markdown 格式）
  python3 format_gongwen.py 报告.docx --markdown   # 同上
        """,
    )
    parser.add_argument("input", help="输入文件路径 (.doc/.docx/.md/.txt)")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument(
        "-m",
        "--markdown",
        action="store_true",
        help="输出为 Markdown 格式（保留 Markdown 符号，仅转换引号）",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误：文件不存在: {input_path}")
        sys.exit(1)

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    elif args.markdown:
        output_path = input_path.with_suffix(".md")
    else:
        output_path = input_path.with_suffix(".txt")

    # 根据模式选择处理函数
    if args.markdown:
        success = format_gongwen_markdown(input_path, output_path)
    else:
        success = format_gongwen_txt(input_path, output_path)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
