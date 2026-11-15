# -*- coding: utf-8 -*-
"""把 docs/md/*.md 编译成《项目开发文档》docx。

用法:
    python docs/build.py            # 生成 docs/../校园文创产品生产管理系统-项目开发文档.docx
    python docs/build.py --check    # 只检查 md 是否都能解析

支持的排版子集:
    # 一级标题（章，另起一页）      ## 二级      ### 三级
    普通段落（首行缩进 2 字符）
    **加粗** 与 `行内代码`
    | 表格 | 表头 |
    - 无序列表 / 1. 有序列表
    ```lang ... ``` 代码块（灰底等宽）
    ![图 2-1 用例图](figs/fig2-1.png)  图片 + 图题（可加 {width=12cm}）
    > 提示块（用于"注"）
"""
import os
import re
import sys
import glob

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
MD = os.path.join(DOCS, "md")
OUT = os.path.join(ROOT, "校园文创产品生产管理系统-项目开发文档.docx")

COVER = {
    "course": "中级软件设计实作",
    "title": "校园文创产品生产管理系统",
    "subtitle": "项目开发文档",
    "topic": "选题方向：课题一  MES 管理系统",
    "fields": [
        ("专    业", "软件工程"),
        ("班    级", "＿＿＿＿＿＿＿＿＿＿"),
        ("姓    名", "＿＿＿＿＿＿＿＿＿＿"),
        ("学    号", "＿＿＿＿＿＿＿＿＿＿"),
        ("指导教师", "＿＿＿＿＿＿＿＿＿＿"),
        ("完成日期", "2026 年 11 月"),
    ],
}


# ---------------------------------------------------------------- 基础排版工具
def set_run_font(run, ascii_font="Times New Roman", east="宋体", size=None,
                 bold=None, color=None):
    run.font.name = ascii_font
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), ascii_font)
    rfonts.set(qn("w:hAnsi"), ascii_font)
    rfonts.set(qn("w:eastAsia"), east)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor(*color)


def shade(cell_or_par, fill):
    el = cell_or_par._tc if hasattr(cell_or_par, "_tc") else cell_or_par._p
    pr = el.get_or_add_tcPr() if hasattr(el, "get_or_add_tcPr") else el.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pr.append(shd)


def add_field(paragraph, instr):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t")
    txt.text = "（请在 Word 中右键选择“更新域”）"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    for el in (fld_begin, instr_el, fld_sep, txt, fld_end):
        run._r.append(el)


def style_doc(doc):
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    pf = st.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.first_line_indent = Pt(24)

    h1 = doc.styles["Heading 1"]
    h1.font.name = "Times New Roman"
    h1.font.size = Pt(16)
    h1.font.bold = True
    h1.font.color.rgb = RGBColor(0, 0, 0)
    h1.element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(12)
    h1.paragraph_format.first_line_indent = Pt(0)
    h1.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    h2 = doc.styles["Heading 2"]
    h2.font.name = "Times New Roman"
    h2.font.size = Pt(14)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor(0, 0, 0)
    h2.element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    h2.paragraph_format.space_before = Pt(6)
    h2.paragraph_format.space_after = Pt(6)
    h2.paragraph_format.first_line_indent = Pt(0)

    h3 = doc.styles["Heading 3"]
    h3.font.name = "Times New Roman"
    h3.font.size = Pt(12)
    h3.font.bold = True
    h3.font.color.rgb = RGBColor(0, 0, 0)
    h3.element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    h3.paragraph_format.space_before = Pt(6)
    h3.paragraph_format.space_after = Pt(3)
    h3.paragraph_format.first_line_indent = Pt(0)

    for sec in doc.sections:
        sec.page_height = Cm(29.7)
        sec.page_width = Cm(21.0)
        sec.top_margin = Cm(2.54)
        sec.bottom_margin = Cm(2.54)
        sec.left_margin = Cm(3.0)
        sec.right_margin = Cm(3.0)


def add_page_number(sec):
    p = sec.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    run = p.add_run()
    for tag, attr, text in (("begin", None, None), ("instr", None, "PAGE"),
                            ("end", None, None)):
        pass
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)
    set_run_font(run, size=10.5)


# ---------------------------------------------------------------- 行内格式
INLINE = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`)")


def add_inline(par, text, base_size=12, base_east="宋体", bold=False):
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            r = par.add_run(part[2:-2])
            set_run_font(r, east=base_east, size=base_size, bold=True)
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            r = par.add_run(part[1:-1])
            set_run_font(r, ascii_font="Consolas", east="宋体", size=base_size - 1.5)
        else:
            r = par.add_run(part)
            set_run_font(r, east=base_east, size=base_size, bold=bold)


# ---------------------------------------------------------------- 块级渲染
def md_to_docx(doc, path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    buf = []
    i = 0
    n = len(lines)

    def flush():
        nonlocal buf
        if not buf:
            return
        text = " ".join(x.strip() for x in buf).strip()
        buf = []
        if not text:
            return
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Pt(24)
        add_inline(p, text)

    while i < n:
        line = lines[i]
        s = line.strip()

        if s.startswith("```"):
            flush()
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.first_line_indent = Pt(0)
            pf.left_indent = Pt(12)
            pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
            pf.space_before = Pt(3)
            pf.space_after = Pt(6)
            shade(p, "F2F2F2")
            r = p.add_run("\n".join(code))
            set_run_font(r, ascii_font="Consolas", east="宋体", size=9)
            continue

        if s.startswith("#"):
            flush()
            level = len(s) - len(s.lstrip("#"))
            title = s[level:].strip()
            p = doc.add_heading(level=min(level, 3))
            p.paragraph_format.first_line_indent = Pt(0)
            if level == 1:
                p.paragraph_format.page_break_before = True
            r = p.add_run(title)
            set_run_font(r, east="黑体", size={1: 16, 2: 14, 3: 12}.get(level, 12),
                         bold=True)
            i += 1
            continue

        if s.startswith("!["):
            flush()
            m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)(?:\{width=([\d.]+)cm\})?", s)
            if m:
                cap, src, width = m.group(1), m.group(2), m.group(3)
                img = os.path.join(DOCS, src)
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.first_line_indent = Pt(0)
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.keep_with_next = bool(cap)
                p.paragraph_format.keep_together = True
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                if os.path.exists(img):
                    p.add_run().add_picture(img, width=Cm(float(width or 15.0)))
                else:
                    r = p.add_run("［缺图：%s］" % src)
                    set_run_font(r, size=10.5)
                if cap:
                    cp = doc.add_paragraph()
                    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    cp.paragraph_format.first_line_indent = Pt(0)
                    cp.paragraph_format.space_after = Pt(6)
                    r = cp.add_run(cap)
                    set_run_font(r, size=10.5, bold=True)
            i += 1
            continue

        if s.startswith("|"):
            flush()
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            rows = [r for r in rows if not re.match(r"^\|[\s:\-|]+\|$", r)]
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            if not cells:
                continue
            ncol = max(len(r) for r in cells)

            # 按内容估算列宽：以字符数开方为权重，限制在 2.2~9.5cm，总宽 15cm
            import math

            def disp(s):
                return sum(2 if ord(ch) > 127 else 1 for ch in s)

            lens = []
            for ci in range(ncol):
                lens.append(max([disp(r[ci]) for r in cells if ci < len(r)] + [5]))
            wts = [math.sqrt(x) for x in lens]
            widths = [15.0 * x / sum(wts) for x in wts]
            MIN, MAX = 2.2, 9.5
            clamped = set()
            for _ in range(8):
                freec = [ci for ci in range(ncol) if ci not in clamped]
                if not freec:
                    break
                rest = 15.0 - sum(widths[ci] for ci in clamped)
                tot = sum(wts[ci] for ci in freec) or 1.0
                for ci in freec:
                    widths[ci] = rest * wts[ci] / tot
                bad = False
                for ci in freec:
                    if widths[ci] < MIN:
                        widths[ci], bad = MIN, True
                        clamped.add(ci)
                    elif widths[ci] > MAX:
                        widths[ci], bad = MAX, True
                        clamped.add(ci)
                if not bad:
                    break
            widths = [Cm(w) for w in widths]

            t = doc.add_table(rows=0, cols=ncol)
            t.style = "Table Grid"
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            t.autofit = False
            for ri, row in enumerate(cells):
                tr = t.add_row()
                for ci in range(ncol):
                    txt = row[ci] if ci < len(row) else ""
                    cell = tr.cells[ci]
                    cell.text = ""
                    p = cell.paragraphs[0]
                    p.paragraph_format.first_line_indent = Pt(0)
                    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                    p.paragraph_format.space_before = Pt(1)
                    p.paragraph_format.space_after = Pt(1)
                    if ri == 0:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        shade(cell, "DCE6F1")
                        add_inline(p, txt, base_size=10.5, bold=True)
                    else:
                        add_inline(p, txt, base_size=10.5)
            for ci, w in enumerate(widths):
                for cell in t.columns[ci].cells:
                    cell.width = w

            tblPr = t._tbl.tblPr
            mar = OxmlElement("w:tblCellMar")
            for side, v in (("top", 10), ("bottom", 10), ("left", 80), ("right", 80)):
                el = OxmlElement("w:%s" % side)
                el.set(qn("w:w"), str(v))
                el.set(qn("w:type"), "dxa")
                mar.append(el)
            tblPr.append(mar)

            cp = doc.add_paragraph()
            cp.paragraph_format.first_line_indent = Pt(0)
            cp.paragraph_format.space_before = Pt(0)
            cp.paragraph_format.space_after = Pt(0)
            cp.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            r = cp.add_run("")
            r.font.size = Pt(6)
            continue

        if s.startswith("> "):
            flush()
            txt = s[2:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.left_indent = Pt(24)
            shade(p, "FFF7E6")
            add_inline(p, txt, base_size=10.5)
            i += 1
            continue

        if re.match(r"^[-*] ", s):
            flush()
            txt = re.sub(r"^[-*] ", "", s)
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.left_indent = Pt(24)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
            add_inline(p, txt)
            i += 1
            continue

        if re.match(r"^\d+\.\s", s):
            flush()
            num, txt = s.split(".", 1)
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.left_indent = Pt(24)
            add_inline(p, num + "." + txt)
            i += 1
            continue

        if not s:
            flush()
            i += 1
            continue

        buf.append(line)
        i += 1

    flush()


# ---------------------------------------------------------------- 封面与目录
def build_cover(doc):
    for _ in range(2):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run("《%s》课程项目" % COVER["course"])
    set_run_font(r, east="黑体", size=18, bold=True)

    for _ in range(2):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run(COVER["title"])
    set_run_font(r, east="黑体", size=30, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run(COVER["subtitle"])
    set_run_font(r, east="黑体", size=22, bold=True)

    for _ in range(2):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run(COVER["topic"])
    set_run_font(r, east="楷体", size=14)

    for _ in range(3):
        doc.add_paragraph()

    for key, val in COVER["fields"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Pt(0)
        p.paragraph_format.space_after = Pt(10)
        r = p.add_run("%s：%s" % (key, val))
        set_run_font(r, east="宋体", size=14)


def build_toc(doc):
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run("目    录")
    set_run_font(r, east="黑体", size=18, bold=True)

    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(0)
    add_field(p, 'TOC \\o "1-2" \\h \\z \\u')


# ---------------------------------------------------------------- main
def main():
    check_only = "--check" in sys.argv
    files = sorted(glob.glob(os.path.join(MD, "ch*.md")))
    if not files:
        print("no markdown under", MD)
        return 1
    if check_only:
        for f in files:
            print("ok", os.path.basename(f), len(open(f, encoding="utf-8").read()))
        return 0

    doc = Document()
    style_doc(doc)
    add_page_number(doc.sections[0])
    build_cover(doc)
    build_toc(doc)

    for f in files:
        md_to_docx(doc, f)

    doc.save(OUT)
    print("saved:", OUT)
    print("chapters:", ", ".join(os.path.basename(f) for f in files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
