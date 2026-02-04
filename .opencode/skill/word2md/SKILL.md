---
name: word2md
description: 将 Word 文档 (.doc/.docx) 转换为干净的 Markdown 格式，包含完整的转换、清理和表格优化流程
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: document-processing
---

## 功能说明

此 skill 提供完整的 Word 转 Markdown 工作流，包含三个处理阶段：

1. **转换阶段** (`word2md.py`) - Word 文档转 Markdown
2. **清理阶段** (`clean_md.py`) - 清理遗留的格式标记
3. **表格优化** (`grid2gfm.py`) - 将 Grid Table 转为 GFM Table

## 使用场景

当用户需要：
- 将 Word 文档转换为 Markdown
- 批量处理多个 Word 文件
- 获得干净、可读的 Markdown 输出
- 表格能在 GitHub/常见 Markdown 渲染器中正确显示

## 依赖要求

- **pandoc**: 文档转换工具 (`brew install pandoc`)
- **textutil**: macOS 内置工具，用于处理 .doc 格式
- **Python 3.10+**: 运行脚本

## 脚本清单

| 脚本 | 功能 | 用法 |
|------|------|------|
| `word2md.py` | Word → Markdown 转换 | `python3 word2md.py <input> [-o output]` |
| `clean_md.py` | 清理遗留标记 | `python3 clean_md.py <input> -i` |
| `grid2gfm.py` | Grid Table → GFM Table | `python3 grid2gfm.py <input> -i` |

## 完整工作流

### 一键执行（推荐）

```bash
python3 word2md.py <输入路径> -o <输出目录> && \
python3 clean_md.py <输出目录> -i && \
python3 grid2gfm.py <输出目录> -i
```

### 分步执行

```bash
# 步骤1: 转换 Word 为 Markdown
python3 word2md.py raw/ -o output/

# 步骤2: 清理遗留标记
python3 clean_md.py output/ -i

# 步骤3: 优化表格格式
python3 grid2gfm.py output/ -i
```

## 执行步骤（AI 助手遵循）

1. **确认输入输出路径**
   - 确认用户要转换的文件或目录
   - 确认输出目录位置

2. **检查依赖**
   - 运行 `which pandoc` 确认已安装
   - 确认项目中存在三个脚本

3. **执行完整流程**
   ```bash
   python3 word2md.py <input> -o <output> && \
   python3 clean_md.py <output> -i && \
   python3 grid2gfm.py <output> -i
   ```

4. **验证结果**
   - 检查输出文件是否生成
   - 抽查 Markdown 内容是否正确
   - 确认表格格式正常

5. **报告结果**
   - 告知用户转换成功的文件数量
   - 如有问题，说明具体情况

## 清理的内容

`clean_md.py` 会清理以下遗留标记：

- `[text]{.s1}` → `text` (span 类标记)
- `{.Apple-converted-space}` (Apple 空格标记)
- `\` 单独的反斜杠行
- `PAGE...MERGEFORMAT` (Word 页码域)
- 多余的空行

## 表格转换

`grid2gfm.py` 将 Pandoc 的 Grid Table 转为标准 GFM Table：

**转换前：**
```
+--------+--------+
| 列1    | 列2    |
+--------+--------+
| 数据1  | 数据2  |
+--------+--------+
```

**转换后：**
```
| 列1 | 列2 |
|---|---|
| 数据1 | 数据2 |
```

## 示例

```
用户: 请把 raw/ 目录下的 Word 文件转换为 Markdown，放到"先进个人"文件夹

助手: 
1. 执行转换流程
   python3 word2md.py raw/ -o 先进个人/ && \
   python3 clean_md.py 先进个人/ -i && \
   python3 grid2gfm.py 先进个人/ -i

2. 报告结果
   - 转换成功: 1 个文件
   - 输出位置: 先进个人/xxx.md
```

## 常见问题

### Q: 表格显示不正常？
A: 确保运行了 `grid2gfm.py` 进行表格格式转换

### Q: 还有乱码标记？
A: 确保运行了 `clean_md.py` 进行清理

### Q: .doc 文件转换失败？
A: 确认系统是 macOS 且 textutil 可用
