---
name: gongwen-format
version: 1.1.0
description: |
  一站式公文格式转换与规范化工具。Use when: 用户要求"Word 转公文"、"转成 TXT"、"Excel 转 Markdown"、"检查公文格式"。
  Produces: 符合公文规范的纯净 TXT 或 Markdown 文件。
---

# 公文格式化 Skill

> 公文格式化不是简单的格式转换，而是让文档"可用"——去除所有技术性标记，输出可直接粘贴使用的纯净文本。

## 触发词路由

| 用户说 | 模式 |
|--------|------|
| "把 Word 转成公文格式" / "转成可用的 TXT" | 模式一 |
| "把 Markdown 转成 TXT" / "去掉 Markdown 格式" | 模式二 |
| "转换引号" / "引号改成全角" | 模式三 |
| "检查公文格式" | 模式四 |
| "Word 转 Markdown" / "转成公文规范的 Markdown" | 模式五 |
| "Excel 转 Markdown" / "xlsx 转 md" | 模式六 |

## 脚本位置

```
项目根目录/
├── word2md.py         # Word → Markdown
├── clean_md.py        # 清理 Pandoc 遗留标记
├── convert_quotes.py  # 半角引号 → 全角引号
├── grid2gfm.py        # Grid Table → GFM Table
└── .opencode/skill/gongwen-format/scripts/
    └── excel2md.py    # Excel → Markdown 表格
```

---

## 模式一：Word → 公文 TXT

**目标**：Word 文档转为可直接粘贴的纯净 TXT。

### 步骤

```bash
# 1. Word → Markdown
python3 word2md.py <input.docx> -o <output_dir>

# 2. 清理遗留标记
python3 clean_md.py <output.md> -i
```

**3. AI 手动处理**（读取 md 文件后执行）：

- 删除 `#`、`##`、`**` 等 Markdown 符号
- 融合小标题到段落：
  ```
  # 错误
  （一）标题。
  
  内容文字……
  
  # 正确
  （一）标题。内容文字……
  ```
- 一级标题（一、二、三）前后保留空行，段落间无空行

**4. 写入临时文件后执行引号转换**：

```bash
python3 convert_quotes.py <temp.md> -o <output.txt>
```

### 验证

- [ ] 无 Markdown 符号（#、**、-）
- [ ] 已执行 convert_quotes.py（不可跳过）
- [ ] 小标题已融入段落
- [ ] 文件格式 .txt

---

## 模式二：Markdown → 公文 TXT

**目标**：Markdown 文件转为纯净 TXT。

### 步骤

1. 读取 Markdown 文件
2. AI 手动删除 Markdown 符号、融合小标题（同模式一）
3. 写入临时文件
4. 执行引号转换：
   ```bash
   python3 convert_quotes.py <temp.md> -o <output.txt>
   ```

### 验证

同模式一。

---

## 模式三：仅引号转换

**目标**：半角引号 → 中文全角引号。

### 步骤

```bash
python3 convert_quotes.py <input_file> -o <output_file>
```

### 输出

- 转换的引号对数
- 未配对引号警告（如有）

---

## 模式四：格式检查

**目标**：检查文档是否符合公文格式规范。

### 步骤

**1. 强制执行引号转换**（不依赖 AI 判断）：

```bash
python3 convert_quotes.py <input_file> -o <input_file>
```

> ⚠️ **红线**：引号检测不可依赖 AI 肉眼判断，必须通过脚本执行。即使 AI 认为"全部是全角引号"，仍必须执行此步骤。

**2. AI 检查其他项目**：

- [ ] 是否有 Markdown 残留符号（#、**、-）？
- [ ] 小标题是否融入段落？
- [ ] 序号层级是否正确（一、→（一）→ 1. →（1））？
- [ ] 一级标题前后是否有空行？

### 输出

1. 报告引号转换数量（来自脚本输出）
2. 生成其他检查项的通过/未通过报告

---

## 模式五：Word → 公文规范 Markdown

**目标**：Word 转 Markdown，保留格式标记，仅规范化引号。

### 步骤

```bash
# 1. Word → Markdown
python3 word2md.py <input.docx> -o <output_dir>

# 2. 清理遗留标记
python3 clean_md.py <output.md> -i

# 3. 表格优化（如有）
python3 grid2gfm.py <output.md> -i

# 4. 引号转换
python3 convert_quotes.py <output.md> -o <output.md>
```

### 输出特点

- ✅ 保留 Markdown 格式符号
- ✅ 引号转为中文全角
- ✅ 表格为 GFM 格式
- ❌ 不融合小标题（保持 Markdown 结构）

---

## 模式六：Excel → Markdown 表格

**目标**：Excel 表格转为 GFM Markdown 表格。

### 步骤

```bash
python3 .opencode/skill/gongwen-format/scripts/excel2md.py <input.xlsx> [output.md]
```

### 脚本功能

- 自动跳过标题行，识别真正表头
- 清理单元格换行符
- 移除全空列
- 生成 GFM 格式表格

### 验证

- [ ] 表头正确识别
- [ ] 数据行数正确
- [ ] 表格格式符合 GFM 规范

### 注意

- 仅支持 `.xlsx`（不支持 `.xls`、`.et`）
- `.et` 格式需先转存为 `.xlsx`

---

## 红线约束

### 引号处理强制规则

1. **禁止依赖 AI 判断引号类型**：AI 无法可靠区分半角引号（\"）和全角引号（""），所有引号相关检查必须通过 `convert_quotes.py` 脚本执行。

2. **写入后必须转换**：任何公文文件（.txt、.md）在以下操作后，必须立即执行引号转换：
   - 使用 Write 工具创建新文件
   - 使用 Edit 工具修改文件
   - AI 手动处理内容后写入文件

   ```bash
   python3 convert_quotes.py <file> -o <file>
   ```

3. **格式检查必须包含脚本调用**：执行模式四（格式检查）时，无论 AI 是否认为引号已经是全角，都必须执行转换脚本。

### 其他红线

4. **不编造数值**：金额、数量、比例等数值必须来自用户提供的素材，不可杜撰。

5. **不使用 Markdown 符号**：公文 TXT 输出中禁止出现 #、**、-、* 等符号。

---

## 公文格式速查

### 禁止内容

| 禁止 | 正确 |
|------|------|
| `# 标题` | `标题` |
| `**文字**` | `文字` |
| `"引号"` | `"引号"` |
| 小标题独立成行 | 融入段落 |

### 序号层级

| 层级 | 格式 | 示例 |
|------|------|------|
| 一级 | 中文数字+顿号 | 一、二、三、 |
| 二级 | 括号中文数字 | （一）（二）（三） |
| 三级 | 阿拉伯数字+点 | 1. 2. 3. |
| 四级 | 括号阿拉伯数字 | （1）（2）（3） |

### 小标题融合示例

**错误**：
```
**（一）突出政治引领。**

坚持把理论学习摆在首位……
```

**正确**：
```
（一）突出政治引领。坚持把理论学习摆在首位……
```
