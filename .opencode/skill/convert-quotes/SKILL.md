---
name: convert-quotes
description: 当用户要求“转换引号”、“半角转全角”、“修复引号”、“引号格式化”、“公文格式化”时使用此Skill。将半角双引号转换为中文全角双引号（“”）。
version: 1.0.0
---

# 引号转换工具

本Skill用于将文本文件中的半角双引号（"）转换为中文全角双引号（“”），确保公文材料符合格式规范。

## 使用场景

- 公文材料撰写后的格式化处理
- Markdown文件转换为可直接粘贴的TXT文件
- 批量修复引号格式问题

## 引号对照表

| 类型 | 字符 | Unicode | 说明 |
|------|------|---------|------|
| 半角双引号 | " | U+0022 | 需要转换 |
| 全角左双引号 | “ | U+201C | 转换目标 |
| 全角右双引号 | ” | U+201D | 转换目标 |
| 半角单引号 | ' | U+0027 | 可选转换 |
| 全角左单引号 | ‘ | U+2018 | 可选目标 |
| 全角右单引号 | ’ | U+2019 | 可选目标 |

## 脚本位置

```
/Users/arnoldwang/01_Active_Projects/Fuck-Work/convert_quotes.py
```

## 用法

### 基本用法

```bash
# 输入 .md 文件，输出 .txt 文件
python3 convert_quotes.py report.md

# 指定输出文件名
python3 convert_quotes.py report.md -o final.txt

# 原地修改（覆盖原文件）
python3 convert_quotes.py report.md -i

# 同时转换单引号
python3 convert_quotes.py report.md --single

# 静默模式
python3 convert_quotes.py report.md -q
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `input` | 输入文件路径（必填） |
| `-o, --output` | 输出文件路径（默认：原文件名.txt） |
| `-i, --inplace` | 原地修改，覆盖原文件 |
| `--single` | 同时转换半角单引号 |
| `-q, --quiet` | 静默模式，减少输出 |

## 转换规则

1. **成对转换**：第1、3、5...个引号转为左引号"，第2、4、6...个引号转为右引号"
2. **奇数警告**：如果引号数量为奇数，脚本会发出警告（可能存在未配对引号）
3. **验证结果**：转换完成后自动验证，确保无遗漏

## 示例输出

```
Input: 年度述职/报告.md
Found 168 half-width double quotes
Output: 年度述职/报告.txt
Converted: 84 left + 84 right
Done.
```

## 与公文撰写Skill的配合

1. 使用 `gongwen` Skill 撰写公文材料
2. 材料保存为 Markdown 文件
3. 使用本工具转换引号，输出为 TXT 文件
4. TXT 文件可直接粘贴使用

## 注意事项

- 脚本依赖 Python 3.6+
- 文件编码必须为 UTF-8
- 建议转换前备份原文件
- 如果引号数量为奇数，请手动检查是否有遗漏
