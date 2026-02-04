#!/usr/bin/env python3
"""
Excel to Markdown converter - 最终优化版
1. 自动检测并跳过标题行
2. 移除单元格内换行符
3. 清理空列
"""
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import re

def parse_xlsx_to_data(xlsx_path):
    """解析 .xlsx 文件，返回数据矩阵"""
    with zipfile.ZipFile(xlsx_path, 'r') as zip_ref:
        # 读取共享字符串
        shared_strings = []
        try:
            with zip_ref.open('xl/sharedStrings.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                for si in root.findall('.//main:si', ns):
                    # 提取所有文本节点（处理换行）
                    texts = []
                    for t in si.findall('.//main:t', ns):
                        if t.text:
                            texts.append(t.text)
                    shared_strings.append(''.join(texts))
        except KeyError:
            pass
        
        # 读取第一个worksheet
        with zip_ref.open('xl/worksheets/sheet1.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            
            rows_data = []
            for row in root.findall('.//main:row', ns):
                row_data = {}
                cells = row.findall('.//main:c', ns)
                
                for cell in cells:
                    cell_ref = cell.get('r')
                    if not cell_ref:
                        continue
                    
                    col_letter = ''.join(c for c in cell_ref if c.isalpha())
                    col_idx = 0
                    for c in col_letter:
                        col_idx = col_idx * 26 + (ord(c) - ord('A') + 1)
                    col_idx -= 1
                    
                    v = cell.find('.//main:v', ns)
                    if v is not None and v.text:
                        t_attr = cell.get('t')
                        if t_attr == 's':
                            idx = int(v.text)
                            if idx < len(shared_strings):
                                cell_value = shared_strings[idx]
                            else:
                                cell_value = v.text
                        else:
                            cell_value = v.text
                    else:
                        cell_value = ''
                    
                    # 清理换行符和多余空格
                    cell_value = str(cell_value).replace('\n', ' ').replace('\r', ' ')
                    cell_value = re.sub(r'\s+', ' ', cell_value).strip()
                    
                    row_data[col_idx] = cell_value
                
                if row_data:
                    rows_data.append(row_data)
            
            return rows_data

def dict_rows_to_matrix(rows_data):
    """将字典行转换为规整的矩阵，并移除全空列"""
    if not rows_data:
        return []
    
    max_col = max(max(row.keys()) for row in rows_data if row)
    
    # 转换为矩阵
    matrix = []
    for row_dict in rows_data:
        row = []
        for col_idx in range(max_col + 1):
            row.append(row_dict.get(col_idx, ''))
        matrix.append(row)
    
    # 检测并移除全空列
    if not matrix:
        return []
    
    num_cols = len(matrix[0])
    cols_to_keep = []
    
    for col_idx in range(num_cols):
        has_content = False
        for row in matrix:
            if col_idx < len(row) and row[col_idx].strip():
                has_content = True
                break
        if has_content:
            cols_to_keep.append(col_idx)
    
    # 创建清理后的矩阵
    clean_matrix = []
    for row in matrix:
        clean_row = [row[col_idx] if col_idx < len(row) else '' for col_idx in cols_to_keep]
        clean_matrix.append(clean_row)
    
    return clean_matrix

def detect_header_row(matrix):
    """检测真正的表头行（包含"序号"等关键词）"""
    if not matrix:
        return 0
    
    for i, row in enumerate(matrix[:5]):  # 只检查前5行
        row_text = ' '.join(str(cell) for cell in row)
        if '序号' in row_text or '编号' in row_text:
            return i
    
    return 0

def format_markdown_table(matrix):
    """格式化为 Markdown 表格"""
    if not matrix or len(matrix) < 2:
        return ""
    
    # 计算每列的最大宽度
    num_cols = len(matrix[0])
    col_widths = [0] * num_cols
    
    for row in matrix:
        for i, cell in enumerate(row):
            if i < num_cols:
                display_width = sum(2 if ord(c) > 127 else 1 for c in str(cell))
                col_widths[i] = max(col_widths[i], display_width, 3)
    
    md_lines = []
    
    # 表头
    if matrix:
        header = matrix[0]
        header_cells = []
        for i, cell in enumerate(header):
            display_width = sum(2 if ord(c) > 127 else 1 for c in str(cell))
            padding = col_widths[i] - display_width
            header_cells.append(str(cell) + ' ' * padding)
        md_lines.append('| ' + ' | '.join(header_cells) + ' |')
    
    # 分隔线
    separator_cells = ['-' * max(3, col_widths[i]) for i in range(num_cols)]
    md_lines.append('| ' + ' | '.join(separator_cells) + ' |')
    
    # 数据行
    for row in matrix[1:]:
        row_cells = []
        for i, cell in enumerate(row):
            if i < num_cols:
                display_width = sum(2 if ord(c) > 127 else 1 for c in str(cell))
                padding = col_widths[i] - display_width
                row_cells.append(str(cell) + ' ' * padding)
        md_lines.append('| ' + ' | '.join(row_cells) + ' |')
    
    return '\n'.join(md_lines)

def convert_excel_to_markdown(input_path, output_path=None):
    """主转换函数"""
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"✗ 文件不存在: {input_path}")
        return None
    
    if input_file.suffix.lower() != '.xlsx':
        print(f"✗ 仅支持 .xlsx 格式")
        return None
    
    try:
        # 解析 Excel
        rows_data = parse_xlsx_to_data(input_path)
        matrix = dict_rows_to_matrix(rows_data)
        
        if not matrix:
            print(f"✗ 未找到数据")
            return None
        
        # 检测表头行
        header_idx = detect_header_row(matrix)
        if header_idx > 0:
            print(f"  检测到表头在第 {header_idx + 1} 行，跳过前 {header_idx} 行标题")
            matrix = matrix[header_idx:]
        
        # 生成 Markdown
        file_name = input_file.stem
        md_content = f"# {file_name}\n\n"
        md_content += format_markdown_table(matrix)
        md_content += "\n"
        
        # 确定输出路径
        if output_path is None:
            output_path = input_file.with_suffix('.md')
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✓ 转换成功")
        print(f"  原文件: {input_path}")
        print(f"  输出: {output_path}")
        print(f"  数据行: {len(matrix) - 1} 行数据 + 1 行表头")
        print(f"  有效列: {len(matrix[0])} 列")
        
        return str(output_path)
        
    except Exception as e:
        print(f"✗ 转换失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 excel2md_final.py <Excel文件路径> [输出路径]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_excel_to_markdown(input_file, output_file)
