# -*- coding: utf-8 -*-
"""生成课程汇报 PPT：校园文创产品生产管理系统（16:9，14 页）。"""
import os
from pptx import Presentation
from pptx.util import Cm, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

NAVY = RGBColor(0x1F, 0x38, 0x64)
BLUE = RGBColor(0x2E, 0x54, 0x96)
GREY = RGBColor(0x59, 0x59, 0x59)
LIGHT = RGBColor(0xE8, 0xEE, 0xF7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FONT = "微软雅黑"

prs = Presentation()
prs.slide_width = Cm(33.867)
prs.slide_height = Cm(19.05)
BLANK = prs.slide_layouts[6]


def tb(slide, x, y, w, h, text, size=18, bold=False, color=GREY, align=PP_ALIGN.LEFT,
       font=FONT, spacing=1.15):
    box = slide.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
    tf = box.text_frame
    tf.word_wrap = True
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = font
    return box


def rect(slide, x, y, w, h, fill=LIGHT, line=None):
    from pptx.enum.shapes import MSO_SHAPE
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Cm(x), Cm(y), Cm(w), Cm(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(1)
    sh.shadow.inherit = False
    sh.adjustments[0] = 0.06
    return sh


def header(slide, title, kicker=None):
    bar = slide.shapes.add_shape(1, Cm(0), Cm(0), Cm(33.867), Cm(1.55))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    bar.shadow.inherit = False
    tb(slide, 1.6, 0.28, 26, 1.0, title, size=22, bold=True, color=WHITE)
    tb(slide, 27.2, 0.45, 5.2, 0.8, kicker or "", size=11, color=RGBColor(0xC9, 0xD6, 0xEA),
       align=PP_ALIGN.RIGHT)


def bullets(slide, x, y, w, items, size=15, gap=0.95, color=GREY, mark="●"):
    for i, it in enumerate(items):
        yy = y + i * gap
        tb(slide, x, yy, 0.8, 0.7, mark, size=size - 4, color=BLUE)
        tb(slide, x + 0.85, yy - 0.06, w, 0.8, it, size=size, color=color)


def table(slide, x, y, w, rows, col_w, head=True, size=11, row_h=0.86):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Cm(x), Cm(y), Cm(w),
                                   Cm(row_h * len(rows)))
    tbl = shape.table
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Cm(cw)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.margin_left = Cm(0.18)
            cell.margin_right = Cm(0.12)
            cell.margin_top = Cm(0.05)
            cell.margin_bottom = Cm(0.05)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            r = p.add_run()
            r.text = val
            r.font.size = Pt(size)
            r.font.name = FONT
            r.font.bold = head and i == 0
            r.font.color.rgb = WHITE if (head and i == 0) else GREY
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY if (head and i == 0) else (
                RGBColor(0xF4, 0xF7, 0xFC) if i % 2 == 0 else WHITE)
    return tbl


# ---------- 1 封面 ----------
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(1, Cm(0), Cm(0), Cm(33.867), Cm(19.05))
bg.fill.solid()
bg.fill.fore_color.rgb = NAVY
bg.line.fill.background()
bg.shadow.inherit = False
tb(s, 2.6, 4.3, 28, 1.0, "《中级软件设计实作》课程项目", size=16, color=RGBColor(0xC9, 0xD6, 0xEA))
tb(s, 2.6, 6.0, 29, 2.2, "校园文创产品生产管理系统", size=44, bold=True, color=WHITE)
tb(s, 2.6, 8.6, 29, 1.2, "基于 IIDP 模型驱动平台的三个 APP", size=20, color=RGBColor(0xC9, 0xD6, 0xEA))
line = s.shapes.add_shape(1, Cm(2.65), Cm(12.4), Cm(6.2), Cm(0.09))
line.fill.solid()
line.fill.fore_color.rgb = RGBColor(0x8F, 0xAA, 0xDC)
line.line.fill.background()
tb(s, 2.6, 13.2, 20, 0.8, "选题方向：课题一  MES 管理系统", size=14, color=RGBColor(0xC9, 0xD6, 0xEA))
tb(s, 2.6, 14.3, 20, 0.8, "软件工程专业    2026 年 11 月", size=14, color=RGBColor(0xC9, 0xD6, 0xEA))

# ---------- 2 背景与痛点 ----------
s = prs.slides.add_slide(BLANK)
header(s, "背景：一个真实的小作坊", "01 项目背景")
tb(s, 1.6, 2.0, 30, 1.0, "学校文创工作室 5 个人，一年做几十款产品：帆布包、校徽、明信片、马克杯。", size=15)
cards = [("编码靠手编", "同一产品在三个表里三个号，月底对不上账"),
         ("BOM 靠记忆", "打样时凭经验领料，多领少领都靠事后补"),
         ("进度靠聊天", "工单状态只存在微信群里，主管不知道做到哪一步")]
for i, (t, d) in enumerate(cards):
    x = 1.7 + i * 10.4
    rect(s, x, 3.5, 9.4, 4.2, LIGHT)
    tb(s, x + 0.5, 3.85, 8.4, 0.9, t, size=17, bold=True, color=NAVY)
    tb(s, x + 0.5, 4.9, 8.4, 2.4, d, size=13, color=GREY)
rect(s, 1.7, 8.6, 30.4, 3.1, RGBColor(0xF4, 0xF7, 0xFC))
tb(s, 2.2, 8.95, 29.4, 0.9, "对应到制造业，就是三件事：编码规则、BOM、工单。", size=16, bold=True, color=NAVY)
tb(s, 2.2, 9.9, 29.4, 1.4,
   "本项目把工作室当车间，用课题一的九条要求做一套“能把东西做出来”的系统；不做商城、不做支付、不做库存台账。", size=13)
tb(s, 1.7, 12.6, 30, 0.9, "范围裁剪的依据：两周工期里，只有主流程跑通才算完成度，周边功能会把时间吃光。", size=13, color=GREY)
tb(s, 1.7, 16.9, 30, 0.8, "校园文创产品生产管理系统  ·  项目汇报", size=10, color=RGBColor(0xAA, 0xAA, 0xAA))

# ---------- 3 目标与九条要求 ----------
s = prs.slides.add_slide(BLANK)
header(s, "把课题九条要求落到一个场景里", "02 项目目标")
rows = [["课题要求", "本项目落地"],
        ["产品管理（名称、规格）", "文创产品：帆布包、校徽、明信片、马克杯"],
        ["物料管理（编码唯一）", "12 安帆布、涤纶线、织唛标签等 20 种"],
        ["产品 BOM 标签页 + 数量", "产品表单内的 BOM 子表，三行明细"],
        ["BOM 添加、删除", "子表内增删行，随主表一次保存"],
        ["编码规则增删改查", "cw-sys 的编码规则页面（前缀、位数、日期格式）"],
        ["按规则生成编码", "codeRuleService.generate，四段式 CP20261115-0118"],
        ["业务模型使用该服务", "产品、物料、工单三类编码统一取号"],
        ["身边的例子", "校园文创工作室（本校真实场景）"],
        ["按模块拆分 APP", "cw-base / cw-prod / cw-sys 三个 jar"]]
table(s, 1.7, 2.05, 30.4, rows, [12.0, 18.4], size=11.5, row_h=1.16)
tb(s, 1.7, 15.5, 30, 0.9, "九条要求逐条对应，答辩时按此表逐项演示。", size=12, color=BLUE)

# ---------- 4 角色与用例 ----------
s = prs.slides.add_slide(BLANK)
header(s, "四类角色，一条主流程", "03 需求")
bullets(s, 1.8, 2.2, 14.5, ["文创设计员：建产品、编 BOM、提打样",
                            "生产主管：审料、下达工单、报完工",
                            "仓库管理员：维护物料、按单备料",
                            "系统管理员：配编码规则、做授权"], size=14, gap=1.15)
rect(s, 17.0, 1.95, 15.4, 4.9, LIGHT)
tb(s, 17.5, 2.25, 14.4, 0.8, "主流程", size=14, bold=True, color=NAVY)
tb(s, 17.5, 3.1, 14.4, 3.4,
   "建产品 → 取编码 → 编 BOM → 下达工单 → 报完工", size=13, color=GREY)
rect(s, 1.8, 7.4, 30.6, 4.4, RGBColor(0xF4, 0xF7, 0xFC))
tb(s, 2.3, 7.7, 29.6, 0.8, "八条业务规则（节选）", size=14, bold=True, color=NAVY)
tb(s, 2.3, 8.5, 29.6, 3.0,
   "BR01 编码四段式全局唯一，生成后不可修改\n"
   "BR04 BOM 每行用量必须大于 0\n"
   "BR05 同一产品同一物料只能出现一次\n"
   "BR08 已完工工单只读，不能再改状态", size=12.5, spacing=1.35)
tb(s, 1.8, 12.5, 30.6, 3.2,
   "需求来源不是拍脑袋：先拆课程要求，再访谈工作室负责人与库管，最后用原型确认。"
   "三条访谈结论直接变成了 BR04、BR05、BR08。", size=13)
tb(s, 1.8, 16.9, 30, 0.8, "校园文创产品生产管理系统  ·  项目汇报", size=10, color=RGBColor(0xAA, 0xAA, 0xAA))

# ---------- 5 总体架构 ----------
s = prs.slides.add_slide(BLANK)
header(s, "四层架构，三个 APP 同进程", "04 设计")
layers = [("用户层", "浏览器 Chrome / Edge，访问 http://localhost:30666/iidp/"),
          ("接入层", "nginx 托管前端 dist，/root/api/* 反向代理到 8061"),
          ("应用层", "IIDP 引擎 v3.0.1（元数据 / ORM / 权限 / 服务）+ cw-base / cw-prod / cw-sys"),
          ("数据层", "MySQL iidp_demo_v3（6 张业务表）· Redis db5")]
for i, (t, d) in enumerate(layers):
    y = 2.3 + i * 3.0
    rect(s, 1.8, y, 30.4, 2.3, LIGHT if i % 2 == 0 else RGBColor(0xF4, 0xF7, 0xFC))
    tb(s, 2.3, y + 0.55, 4.6, 1.2, t, size=14, bold=True, color=NAVY)
    tb(s, 7.2, y + 0.6, 24.6, 1.3, d, size=12.5, color=GREY)
rect(s, 1.8, 14.6, 30.4, 2.3, RGBColor(0xFF, 0xF4, 0xE5))
tb(s, 2.3, 15.0, 29.6, 1.6,
   "刻意不做微服务：三个 APP 独立打包，但跑在同一个引擎进程里。两周工期引不进注册中心与网关，"
   "边界已经用包与 jar 表达清楚了。", size=12.5, color=RGBColor(0x8A, 0x5A, 0x00))

# ---------- 6 APP 拆分与数据模型 ----------
s = prs.slides.add_slide(BLANK)
header(s, "一个 APP 一个包，六个模型", "05 设计")
boxes = [("cw-base", "product / material / product_bom", "主数据"),
         ("cw-prod", "work_order", "生产"),
         ("cw-sys", "code_rule / code_seq", "编码")]
for i, (name, models, tag) in enumerate(boxes):
    x = 1.8 + i * 10.5
    rect(s, x, 2.1, 9.6, 3.6, LIGHT)
    tb(s, x + 0.45, 2.35, 8.7, 0.8, name, size=15, bold=True, color=NAVY)
    tb(s, x + 0.45, 3.2, 8.7, 1.2, models, size=10.5, color=GREY)
    tb(s, x + 0.45, 4.5, 8.7, 0.7, tag, size=10.5, color=BLUE)
rows = [["表", "关键字段", "约束"],
        ["cw_product", "code / name / spec / status", "编码唯一，产品名非空"],
        ["cw_product_bom", "product_id / material_id / amount", "用量 > 0，同产品同物料唯一"],
        ["cw_work_order", "code / product_id / plan_qty / status", "状态 1→2→3 受控"],
        ["cw_code_rule", "rule_code / prefix / seq_len / date_format", "前缀 + 日期段 + 定长流水"],
        ["cw_code_seq", "rule_code / date_seg / curr_value", "规则 + 日期段唯一索引"]]
table(s, 1.8, 6.3, 30.4, rows, [7.4, 14.0, 9.0], size=10.5, row_h=1.05)
tb(s, 1.8, 12.8, 30.4, 2.4,
   "跨 APP 引用不在代码里 import 对方模型类（两个 APP 由不同类加载器加载，运行时抛 ClassNotFound），"
   "而是声明 @ManyToOne(targetModel = \"product\") BaseModel product，由引擎按模型名解析。", size=12.5)

# ---------- 7 编码服务 ----------
s = prs.slides.add_slide(BLANK)
header(s, "编码服务：从静态计数器到行锁取号", "06 实现")
tb(s, 1.8, 2.0, 30.4, 0.9, "参考程序的 CodeGenerator 用静态自增变量，进程重启归零、多实例必然重号，撑不起“按规则配置生成”。", size=12.5)
steps = [("1 校验规则", "按 ruleCode 查 cw_code_rule，不存在或停用直接抛业务异常"),
         ("2 算日期段", "按 date_format 格式化当天，日期段同时是流水重置边界"),
         ("3 行锁取号", "事务内 SELECT curr_value FROM cw_code_seq WHERE rule_code=? AND date_seg=? FOR UPDATE"),
         ("4 拼装编码", "前缀 + 日期段 + 分隔符 + 左补零流水，例如 CP20261115-0118")]
for i, (t, d) in enumerate(steps):
    y = 3.1 + i * 2.55
    rect(s, 1.8, y, 30.4, 2.05, LIGHT if i % 2 == 0 else RGBColor(0xF4, 0xF7, 0xFC))
    tb(s, 2.3, y + 0.5, 6.2, 1.0, t, size=13, bold=True, color=NAVY)
    tb(s, 8.0, y + 0.5, 23.6, 1.2, d, size=11.5, color=GREY)
rect(s, 1.8, 13.5, 30.4, 2.6, RGBColor(0xE8, 0xF3, 0xE9))
tb(s, 2.3, 13.8, 29.6, 2.0,
   "实测：单线程连续 5 次 → 0119–0123；20 线程并发 → 20 个编码互不重复；"
   "preview 预览 0144 后 generate 仍取 0144，预览不占号。", size=12.5, color=RGBColor(0x1E, 0x5B, 0x28))

# ---------- 8 BOM 与工单 ----------
s = prs.slides.add_slide(BLANK)
header(s, "BOM 子表与工单状态机", "07 实现")
rect(s, 1.8, 2.0, 14.8, 6.6, LIGHT)
tb(s, 2.3, 2.3, 13.8, 0.8, "BOM：主子表同页保存", size=13.5, bold=True, color=NAVY)
tb(s, 2.3, 3.2, 13.8, 5.0,
   "· 产品表单内的“BOM 清单”标签页，标题带行数\n"
   "· 增删行在页面内完成，保存时随主表一次提交\n"
   "· 服务层校验：用量 > 0、同产品同物料唯一\n"
   "· 校验走原生 SQL，因 @ManyToOne 字段用 Filter 过滤恒空", size=11.5, spacing=1.5)
rect(s, 17.4, 2.0, 14.8, 6.6, RGBColor(0xF4, 0xF7, 0xFC))
tb(s, 17.9, 2.3, 13.8, 0.8, "工单：三态、单向、有例外", size=13.5, bold=True, color=NAVY)
tb(s, 17.9, 3.2, 13.8, 5.0,
   "· 1 草稿 → 2 已下达 → 3 已完工\n"
   "· 已下达可撤回为草稿，已完工不可回退\n"
   "· 草稿直接完工被拒：提示“草稿不能直接变更为已完工”\n"
   "· 完工数量不得超过计划数量", size=11.5, spacing=1.5)
rows = [["场景", "服务调用", "返回"],
        ["新增产品", "productService.createWithCode", "CP20261115-0118"],
        ["追加 BOM", "productService.addBom × 3", "3 行入库"],
        ["重复物料", "productService.addBom", "拒绝：物料已存在"],
        ["下达工单", "workOrderService.changeStatus", "status=2"],
        ["完工回退", "workOrderService.changeStatus", "拒绝：已完工不能变更"]]
table(s, 1.8, 9.2, 30.4, rows, [6.4, 13.6, 10.4], size=10.5, row_h=0.95)

# ---------- 9 测试结果 ----------
s = prs.slides.add_slide(BLANK)
header(s, "12 条用例，接口级全部通过", "08 验证")
rows = [["编号", "用例", "实际结果"],
        ["TC-01/02", "新增产品 / 名称必填", "生成 CP20261115-0118；空名被拦截"],
        ["TC-03/04", "新增 3 行 BOM / 用量为 0", "3 行入库；用量 0 被拒"],
        ["TC-05/06", "重复物料 / BOM 汇总", "重复被拒；count=3"],
        ["TC-07", "连续生成 5 个编码", "0119–0123 连续无重复"],
        ["TC-08", "20 线程并发取号", "20/20 唯一，无跳号"],
        ["TC-09/10", "草稿直完工 / 完工回退", "均被拒绝，提示明确"],
        ["TC-11/12", "预览不占号 / 未配规则", "预览 0144 后取 0144；未配规则报错"]]
table(s, 1.8, 2.0, 30.4, rows, [4.6, 10.8, 15.0], size=11, row_h=1.25)
tb(s, 1.8, 12.0, 30.4, 3.4,
   "执行方式：脚本登录取 token，用 JSON-RPC 直接调三个 APP 的服务，逐条比对返回值，结果可复现。\n"
   "这一步同时暴露了两个平台缺陷：标准 create 服务取不到记录列表；@Service 独立类不会被注册。", size=12.5)

# ---------- 10 难点 ----------
s = prs.slides.add_slide(BLANK)
header(s, "四个真正卡住我的地方", "09 过程")
items = [("重复 jar 导致引擎启动即崩", "apps/modules 混入 UAT 重复版本与 mes 示例 jar，装载器解析出 null，NPE 打在 AppProcessor.toMap；清理为 11+3 个 jar 后正常"),
         ("自定义服务不被扫描", "引擎的 ServiceLoader 只遍历 @Model 类上的注解，独立 @Service 类不注册；在每个模型类上补 @MethodService 委托"),
         ("并发取号三版演进", "静态计数器 → 唯一索引重试 → 行锁 + 事务；最终 20 线程零重号"),
         ("关联字段查不到、写不进", "Filter 过滤 @ManyToOne 恒空，改原生 SQL；写关联字段必须传主键字符串，传实例会抛 NotSerializable")]
for i, (t, d) in enumerate(items):
    y = 1.95 + i * 3.85
    rect(s, 1.8, y, 30.4, 3.35, LIGHT if i % 2 == 0 else RGBColor(0xF4, 0xF7, 0xFC))
    tb(s, 2.3, y + 0.35, 29.6, 0.8, t, size=13.5, bold=True, color=NAVY)
    tb(s, 2.3, y + 1.25, 29.6, 1.9, d, size=11.5, color=GREY)

# ---------- 11 踩过的坑：菜单为空 ----------
s = prs.slides.add_slide(BLANK)
header(s, "最花时间的坑：菜单为什么是空的", "10 排错")
rect(s, 1.8, 2.0, 30.4, 3.3, RGBColor(0xFF, 0xF4, 0xE5))
tb(s, 2.3, 2.3, 29.6, 0.8, "现象：能登录、能查库，就是没有菜单", size=14, bold=True, color=RGBColor(0x8A, 0x5A, 0x00))
tb(s, 2.3, 3.1, 29.6, 2.0,
   "admin_000001 进得去主界面，左侧菜单为空；base/ui_menu/loadMenu 返回空数组，"
   "课程自带的 implementer 账号同一接口返回 36 条平台菜单——说明链路本身通，是授权没给到。", size=12)
tb(s, 1.8, 5.6, 30.4, 0.8, "排除过的方向（都没用）", size=13.5, bold=True, color=NAVY)
tb(s, 2.3, 6.4, 29.6, 2.4,
   "补 48 条 @View 授权码、2646 条 rbac_role_permission、27 条 Menu + 9 条 ProductLine 的 tenant_function_auth；\n"
   "改 meta_app 的 view_file 与 global；切租户；直接改 SPA 路由——全都无效。", size=12, spacing=1.5)
rect(s, 1.8, 9.0, 30.4, 3.2, RGBColor(0xE8, 0xF3, 0xE8))
tb(s, 2.3, 9.3, 29.6, 0.8, "真相：rbac_role_auth 缺应用级授权", size=14, bold=True, color=RGBColor(0x2E, 0x6B, 0x2E))
tb(s, 2.3, 10.1, 29.6, 2.0,
   "反编译 UiMenu.getPermissionMenu 后顺着链路查到：菜单先按“角色 + APP + tag”做应用级过滤，"
   "自研三个 APP 缺 3 条 app_all=1 的记录。补上后 loadMenu 立刻返回 9 个菜单，页面全部渲染。", size=12)

# ---------- 12 工程与部署 ----------
s = prs.slides.add_slide(BLANK)
header(s, "工程结构、构建与部署", "11 实现")
tb(s, 1.8, 1.95, 15.4, 0.8, "工程结构", size=13.5, bold=True, color=NAVY)
tree = ("sie-iidp-demo-apps/\n"
        "  ├ sie-snest-cw-base   product/material/bom\n"
        "  ├ sie-snest-cw-prod   work_order\n"
        "  └ sie-snest-cw-sys    code_rule/code_seq + 服务\n"
        "apps/modules/  3 个 jar 自动落盘")
tb(s, 1.9, 2.75, 15.0, 3.4, tree, size=10.5, font="Consolas")
tb(s, 18.0, 1.95, 14.2, 0.8, "构建与启动", size=13.5, bold=True, color=NAVY)
tb(s, 18.1, 2.75, 14.0, 3.4,
   "mvn -s settings.xml -o -DskipTests package\n"
   "→ 11 官方 + 3 自研 jar\n"
   "→ java -jar sie-iidp-demo-start.jar\n"
   "→ 约 20 秒监听 8061", size=10.5, font="Consolas")
rows = [["环节", "配置", "值"],
        ["数据库", "dbcp.properties", "MySQL 127.0.0.1:3306 / iidp_demo_v3"],
        ["元数据", "engine.store.meta.mode", "CLOUD（改源码必须重新打包）"],
        ["前端", "nginx", "30666 托管 dist，/root/api/* → 8061"],
        ["权限", "sie_iidp_iam.auth.ignore", "false（交付前已改回并重打包）"]]
table(s, 1.8, 6.4, 30.4, rows, [5.0, 12.0, 13.4], size=10.5, row_h=1.0)
tb(s, 1.8, 11.6, 30.4, 3.0,
   "踩过的坑：改配置文件必须重新打包才生效（早期多次“改配置无效”由此而来）；"
   "重启前必须先停 java，否则 apps/modules 下的 jar 被占用，构建报“另一个程序正在使用此文件”。", size=12)

# ---------- 13 分工与进度 ----------
s = prs.slides.add_slide(BLANK)
header(s, "单人项目，按角色切换", "12 分工")
rows = [["角色", "承担阶段", "交付物"],
        ["需求分析", "M0–M1", "需求调查表、用例图、功能清单"],
        ["系统设计", "M1–M2", "概要设计、详细设计、类图与时序图"],
        ["后端开发", "M2–M4", "22 个源文件、3 个 jar、8 个服务"],
        ["测试", "M4–M5", "12 条用例、缺陷记录"],
        ["文档与演示", "全程", "开发文档、演示脚本、汇报 PPT"]]
table(s, 1.8, 2.0, 30.4, rows, [6.6, 6.0, 17.8], size=11, row_h=1.3)
tb(s, 1.8, 10.0, 30.4, 1.0, "六阶段进度：11-15 启动 → 11-29 截止，共 14 天，累计投入约 62 小时。", size=12.5)
rect(s, 1.8, 11.2, 30.4, 2.4, LIGHT)
tb(s, 2.3, 11.5, 29.6, 1.8,
   "单人最容易出现的问题是“一个人干所有事，但每件事都干不透”。做法是把工作按角色拆开，"
   "每个阶段只戴一顶帽子，交付物通过后再换下一顶。", size=12)

# ---------- 14 总结 ----------
s = prs.slides.add_slide(BLANK)
header(s, "做完的与没做完的", "13 总结")
rect(s, 1.8, 2.0, 14.8, 6.2, LIGHT)
tb(s, 2.3, 2.3, 13.8, 0.8, "做完的", size=14, bold=True, color=NAVY)
tb(s, 2.3, 3.15, 13.8, 4.8,
   "· 三个 APP、六个模型、八个服务\n"
   "· 编码服务并发零重号\n"
   "· 12 条用例接口级全部通过\n"
   "· 三个业务页面真实渲染并截图\n"
   "· 55 页开发文档 + 10 章结构", size=11.5, spacing=1.5)
rect(s, 17.4, 2.0, 14.8, 6.2, RGBColor(0xFF, 0xF4, 0xE5))
tb(s, 17.9, 2.3, 13.8, 0.8, "没做完的", size=14, bold=True, color=RGBColor(0x8A, 0x5A, 0x00))
tb(s, 17.9, 3.15, 13.8, 4.8,
   "· 开发者中心模型/菜单管理本机不可用\n"
   "  （meta_model、meta_menu 无数据）\n"
   "· 权限矩阵只验证了应用级授权这一层", size=11.5, spacing=1.5)
tb(s, 1.8, 9.0, 30.4, 1.2, "最大的收获不是写了多少代码，而是把“平台给的默认行为”一条条验证了一遍。", size=14, bold=True, color=NAVY)
tb(s, 1.8, 10.4, 30.4, 3.4,
   "标准 create 服务不可用、@Service 不注册、Filter 过滤关联字段恒空——这些都不是文档里写的，"
   "只能靠读字节码、二分法、抓请求一条条试出来。这部分经验写在 6.8 与 9.2，"
   "也是这个项目里最像真实工程的部分。", size=12)
tb(s, 1.8, 16.6, 30, 0.8, "谢谢，请老师批评指正", size=13, color=BLUE)

out = r"E:\projects\iidp-demo-3.0\校园文创产品生产管理系统-项目汇报.pptx"
prs.save(out)
print("saved", out, os.path.getsize(out))
