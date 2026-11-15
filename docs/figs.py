# -*- coding: utf-8 -*-
"""生成开发文档所用的配图（PNG，300dpi），输出到 docs/figs/。

用法：python docs/figs.py
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "docs", "figs")
os.makedirs(FIG, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

NAVY = "#1F3864"
BLUE = "#2E5496"
LIGHT = "#E8EEF7"
LIGHT2 = "#F4F6FA"
GREY = "#666666"


CM = 1 / 2.54  # 画布单位按厘米计：figsize 英寸 = 厘米 / 2.54


def canvas(w, h):
    fig = plt.figure(figsize=(w * CM, h * CM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    ax.set_aspect("equal")
    return fig, ax


def box(ax, x, y, w, h, text, fill=LIGHT, edge=NAVY, fs=10.5, rounded=0.12,
        bold=False, color=NAVY, lw=1.2):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.02,rounding_size=%.2f" % rounded,
                       fc=fill, ec=edge, lw=lw, zorder=3)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=color, zorder=4, linespacing=1.5,
            fontweight="bold" if bold else "normal")


def rect(ax, x, y, w, h, text=None, fill="none", edge=NAVY, fs=10, lw=1.2,
         dashed=False, color=NAVY, va="top"):
    p = Rectangle((x, y), w, h, fc=fill, ec=edge, lw=lw, zorder=2,
                  ls=(0, (5, 3)) if dashed else "-")
    ax.add_patch(p)
    if text:
        if va == "top":
            ax.text(x + w / 2, y + h - 0.22, text, ha="center", va="top",
                    fontsize=fs, color=color, fontweight="bold", zorder=3)
        else:
            ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                    fontsize=fs, color=color, zorder=3)


def ell(ax, cx, cy, w, h, text, fill=LIGHT2, edge=BLUE, fs=10, lw=1.1):
    ax.add_patch(Ellipse((cx, cy), w, h, fc=fill, ec=edge, lw=lw, zorder=3))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color="#222222",
            zorder=4, linespacing=1.4)


def actor(ax, x, y, label_text, fs=10):
    """火柴人，x,y 为脚底中点。"""
    r = 0.16
    ax.add_patch(Ellipse((x, y + 1.06), 2 * r, 2 * r, fc="white", ec=NAVY, lw=1.2,
                         zorder=3))
    ax.plot([x, x], [y + 0.72, y + 0.28], color=NAVY, lw=1.2, zorder=3)
    ax.plot([x - 0.28, x + 0.28], [y + 0.60, y + 0.60], color=NAVY, lw=1.2, zorder=3)
    ax.plot([x, x - 0.22], [y + 0.28, y], color=NAVY, lw=1.2, zorder=3)
    ax.plot([x, x + 0.22], [y + 0.28, y], color=NAVY, lw=1.2, zorder=3)
    ax.text(x, y - 0.12, label_text, ha="center", va="top", fontsize=fs,
            color=NAVY, fontweight="bold")


def arrow(ax, p1, p2, style="-|>", ls="-", color=NAVY, lw=1.1, text=None,
          fs=8.5, rad=0.0, tpos=0.5, toff=(0, 0.12)):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=11,
                                 color=color, lw=lw, ls=ls, zorder=5,
                                 connectionstyle="arc3,rad=%.2f" % rad,
                                 shrinkA=1, shrinkB=1))
    if text:
        tx = p1[0] + (p2[0] - p1[0]) * tpos + toff[0]
        ty = p1[1] + (p2[1] - p1[1]) * tpos + toff[1]
        ax.text(tx, ty, text, ha="center", va="center", fontsize=fs, color=GREY,
                bbox=dict(fc="white", ec="none", pad=0.6), zorder=6)


def label(ax, x, y, s, fs=10, color=NAVY, bold=True, ha="center", va="center",
          rot=0):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, rotation=rot,
            fontweight="bold" if bold else "normal", zorder=6)


def save(fig, name, ax=None, crop=None, k=1.0):
    if crop and ax is not None:
        ax.set_xlim(crop[0], crop[1])
        ax.set_ylim(crop[2], crop[3])
        fig.set_size_inches((crop[1] - crop[0]) * CM, (crop[3] - crop[2]) * CM)
    if k != 1.0:
        import matplotlib.text as mtext
        for t in fig.findobj(mtext.Text):
            t.set_fontsize(t.get_fontsize() * k)
    out = os.path.join(FIG, name)
    fig.savefig(out, dpi=300, bbox_inches="tight", pad_inches=0.08,
                facecolor="white")
    plt.close(fig)
    print("saved", out)


# ------------------------------------------------------------------ 图 2-1 用例图
def fig2_1():
    W, H = 13.6, 8.5
    fig, ax = canvas(W, H)

    rect(ax, 3.05, 1.15, 7.95, 6.45, None, fill="#FCFDFF", edge=NAVY, lw=1.3)
    label(ax, 7.00, 8.05, "校园文创产品生产管理系统", fs=11)

    left = [(5.30, 6.85, "维护文创产品"),
            (5.30, 5.85, "维护产品BOM"),
            (5.30, 4.75, "下达生产工单"),
            (5.30, 3.80, "确认完工入库"),
            (5.30, 2.05, "维护物料资料")]
    right = [(9.05, 6.85, "配置编码规则"),
             (9.05, 5.25, "生成业务编码"),
             (9.05, 3.00, "角色与菜单授权")]

    for cx, cy, t in left + right:
        ell(ax, cx, cy, 3.30, 0.92, t, fs=8.6)

    actor(ax, 1.45, 6.85, "文创设计员", fs=8.6)
    actor(ax, 1.45, 4.00, "生产主管", fs=8.6)
    actor(ax, 1.45, 1.75, "仓库管理员", fs=8.6)
    actor(ax, 12.35, 4.05, "系统管理员", fs=8.6)

    arrow(ax, (1.73, 7.45), (3.62, 6.98), style="-")
    arrow(ax, (1.73, 7.45), (3.62, 6.00), style="-")
    arrow(ax, (1.73, 4.60), (3.62, 4.82), style="-")
    arrow(ax, (1.73, 4.60), (3.62, 3.90), style="-")
    arrow(ax, (1.73, 2.35), (3.62, 2.12), style="-")
    arrow(ax, (12.07, 4.65), (10.72, 6.78), style="-")
    arrow(ax, (12.07, 4.65), (10.72, 3.10), style="-")

    arrow(ax, (6.62, 6.70), (7.50, 5.62), style="-|>", ls=(0, (4, 3)), rad=-0.12)
    arrow(ax, (6.62, 5.72), (7.50, 5.45), style="-|>", ls=(0, (4, 3)), rad=-0.06)
    arrow(ax, (6.62, 4.62), (7.50, 5.20), style="-|>", ls=(0, (4, 3)), rad=0.06)

    save(fig, "fig2-1_usecase.png", ax, (0.10, 13.55, 1.20, 8.35), k=0.92)


# ------------------------------------------------------------------ 实体框（ER / 类图）
def entity(ax, x, y, w, title, attrs, header_fill=NAVY, fs=9.5, lh=0.46,
           body_fill="white", pk=None):
    h = 0.58 + lh * len(attrs) + 0.20
    ax.add_patch(Rectangle((x, y), w, h, fc=body_fill, ec=NAVY, lw=1.1, zorder=3))
    ax.add_patch(Rectangle((x, y + h - 0.58), w, 0.58, fc=header_fill, ec=NAVY,
                           lw=1.1, zorder=4))
    ax.text(x + w / 2, y + h - 0.29, title, ha="center", va="center", fontsize=fs,
            color="white", fontweight="bold", zorder=5)
    for i, a in enumerate(attrs):
        yy = y + h - 0.58 - lh * (i + 0.5) - 0.02
        ax.text(x + 0.14, yy, a, ha="left", va="center", fontsize=fs - 0.4,
                color="#222222", zorder=5)
    return (x, y, w, h)


# ------------------------------------------------------------------ 图 4-1 总体架构
def fig4_1():
    W, H = 13.2, 8.9
    fig, ax = canvas(W, H)

    bands = [
        ("用户层", 7.70, 0.95, "浏览器（Chrome / Edge）\nhttp://localhost:30666/iidp/"),
        ("接入层", 6.40, 0.95, "nginx  ·  静态资源托管 + 接口反向代理（30666 → 8061）"),
        ("应用层", 3.55, 2.55, ""),
        ("数据层", 1.60, 1.10, "MySQL（iidp_demo_v3）  ·  Redis（db5）"),
    ]
    for name, y, h, text in bands:
        ax.add_patch(Rectangle((1.5, y), 10.6, h, fc=LIGHT2, ec=NAVY, lw=1.1, zorder=2))
        ax.text(0.65, y + h / 2, name, ha="center", va="center", fontsize=10.5,
                color=NAVY, fontweight="bold")
        if text:
            ax.text(6.80, y + h / 2, text, ha="center", va="center", fontsize=9.5,
                    color="#222222", zorder=3)

    label(ax, 6.80, 5.90, "IIDP 引擎 v3.0.1（Java 8，端口 8061）",
          fs=9.5)

    svc = ["元数据中心\n模型 / 视图", "ORM 与\n数据访问", "权限中心\n角色 / 菜单",
           "服务扩展\n@Service"]
    bw, bh = 2.44, 0.80
    for i, s in enumerate(svc):
        box(ax, 1.75 + i * 2.58, 4.64, bw, bh, s, fs=8.8)

    apps = [("cw-base 主数据", 1.75), ("cw-prod 生产", 4.55), ("cw-sys 编码配置", 7.35)]
    for t, x in apps:
        box(ax, x, 3.72, 2.75, 0.72, t, fill=LIGHT, fs=8.0)
    label(ax, 12.95, 4.21, "业务 APP", fs=7.6, bold=True)

    for y1, y2 in ((7.66, 7.39), (6.36, 6.13), (3.50, 2.66)):
        arrow(ax, (6.80, y1), (6.80, y2), style="<|-|>", lw=1.0)

    save(fig, "fig4-1_arch.png", ax, (0.15, 13.05, 1.40, 8.80), k=0.75)


# ------------------------------------------------------------------ 图 4-3 功能结构
def fig4_2():
    W, H = 13.2, 6.6
    fig, ax = canvas(W, H)

    box(ax, 3.95, 5.62, 5.3, 0.72, "校园文创产品生产管理系统", fs=9.6)
    groups = [("cw-base 主数据", 0.55), ("cw-prod 生产", 4.60),
              ("cw-sys 配置", 8.65)]
    for t, x in groups:
        box(ax, x, 4.35, 4.0, 0.68, t, fs=9.0)
        arrow(ax, (6.60, 5.58), (x + 2.0, 5.06), style="-")

    leaves = {
        0.55: ["产品管理", "BOM 维护", "物料管理"],
        4.60: ["工单管理", "工单下达", "完工查询"],
        8.65: ["编码规则", "编码流水", "角色授权"],
    }
    for x, items in leaves.items():
        trunk = x + 0.28
        ax.plot([trunk, trunk], [4.32, 1.42], color=NAVY, lw=1.0, zorder=3)
        for i, it in enumerate(items):
            y = 3.20 - i * 1.10
            box(ax, x + 0.62, y, 3.1, 0.66, it, fill=LIGHT2, edge=BLUE, fs=9.0,
                bold=False, color="#222222")
            arrow(ax, (trunk, y + 0.33), (x + 0.60, y + 0.33), style="-")

    save(fig, "fig4-2_func.png", ax, (0.35, 13.00, 1.20, 6.50), k=0.92)


# ------------------------------------------------------------------ 图 4-4 ER 图
def fig4_3():
    W, H = 13.2, 7.9
    fig, ax = canvas(W, H)

    entity(ax, 0.45, 5.00, 3.45, "文创产品", ["id", "code 编码", "name 名称", "spec 规格"])
    entity(ax, 9.30, 5.00, 3.45, "物料", ["id", "code 编码", "name 名称", "unit 单位"])
    entity(ax, 4.88, 3.70, 3.45, "产品 BOM", ["id", "product_id", "material_id", "amount 用量"])
    entity(ax, 0.45, 1.40, 3.45, "生产工单", ["id", "code 编码", "product_id", "status 状态"])
    entity(ax, 9.30, 1.40, 3.45, "编码规则", ["id", "rule_key", "prefix 前缀", "seq_len 位数"])
    entity(ax, 4.88, 0.45, 3.45, "编码流水", ["id", "rule_key", "date_seg", "curr_value"])

    arrow(ax, (3.92, 6.55), (4.86, 5.75), style="-")
    label(ax, 4.16, 6.62, "1", fs=8)
    label(ax, 4.66, 5.95, "N", fs=8)
    arrow(ax, (9.30, 6.05), (8.36, 5.95), style="-")
    label(ax, 9.05, 6.22, "1", fs=8)
    label(ax, 8.58, 5.78, "N", fs=8)
    arrow(ax, (2.15, 4.96), (2.15, 4.08), style="-")
    label(ax, 2.42, 4.62, "1", fs=8)
    label(ax, 2.42, 4.12, "N", fs=8)
    arrow(ax, (9.30, 2.10), (8.35, 1.55), style="-")
    label(ax, 9.02, 2.22, "1", fs=8)
    label(ax, 8.56, 1.32, "N", fs=8)

    save(fig, "fig4-3_er.png", ax, (0.30, 13.00, 0.30, 7.80), k=0.86)


# ------------------------------------------------------------------ 图 4-2 组织结构与角色
def fig4_4():
    W, H = 13.4, 6.2
    fig, ax = canvas(W, H)

    box(ax, 4.75, 4.95, 3.9, 0.85, "校园文创工作室\n负责人（生产主管）", fs=10.2)
    kids = [("设计组\n文创设计员", 0.55), ("制作组\n（负责人兼）", 3.55),
            ("库房\n仓库管理员", 6.55), ("信息中心\n系统管理员", 9.55)]
    ax.plot([6.70, 6.70], [4.92, 4.42], color=NAVY, lw=1.0, zorder=3)
    ax.plot([1.90, 11.50], [4.42, 4.42], color=NAVY, lw=1.0, zorder=3)
    for t, x in kids:
        box(ax, x, 3.05, 2.70, 1.00, t, fill=LIGHT2, edge=BLUE, fs=9.6, bold=False,
            color="#222222")
        ax.plot([x + 1.35, x + 1.35], [4.42, 4.08], color=NAVY, lw=1.0, zorder=3)

    label(ax, 6.70, 2.55, "说明：制作组在系统中不单独设角色，“报完工”由生产主管执行；"
                          "信息中心仅维护编码规则与账号授权。", fs=9, bold=False,
          color=GREY)

    save(fig, "fig4-4_org.png", ax, (0.30, 13.10, 2.20, 6.10), k=0.85)



# ------------------------------------------------------------------ 图 5-1 类图
def fig5_1():
    W, H = 13.2, 8.3
    fig, ax = canvas(W, H)

    entity(ax, 0.45, 4.95, 3.8, "Product 产品",
           ["code 编码", "name 名称", "spec 规格", "status 状态",
            "productBomList"])
    entity(ax, 4.75, 4.95, 3.8, "WorkOrder 工单",
           ["code 编码", "product 产品", "planQty 计划数", "status 状态"])
    entity(ax, 9.05, 4.95, 3.8, "Material 物料",
           ["code 编码", "name 名称", "unit 单位", "status 状态"])
    entity(ax, 0.45, 0.85, 3.8, "CodeRule 编码规则",
           ["ruleCode 规则标识", "prefix 前缀", "seqLength 位数", "enabled 启用"])
    entity(ax, 4.75, 0.85, 3.8, "ProductBom BOM",
           ["product 产品", "material 物料", "amount 用量"])
    entity(ax, 9.05, 0.85, 3.8, "CodeSeq 流水",
           ["ruleCode 规则标识", "dateSeg 日期段", "currValue 当前值"])

    arrow(ax, (2.35, 4.92), (5.10, 3.62), style="-|>")
    label(ax, 3.05, 4.62, "1..*", fs=7.6, bold=False)
    arrow(ax, (10.95, 4.92), (8.45, 3.62), style="-|>")
    label(ax, 10.20, 4.62, "1..*", fs=7.6, bold=False)
    arrow(ax, (2.35, 3.60), (2.35, 2.62), style="-|>")
    label(ax, 2.75, 3.10, "1..*", fs=7.6, bold=False)

    save(fig, "fig5-1_class.png", ax, (0.20, 13.10, 0.30, 8.30), k=0.92)


# ------------------------------------------------------------------ 图 5-2 编码生成时序图
def fig5_2():
    W, H = 13.2, 7.4
    fig, ax = canvas(W, H)

    lifes = [(2.05, "产品/工单表单"), (5.55, "codeRuleService"),
             (9.05, "cw_code_rule"), (12.05, "cw_code_seq")]
    for x, t in lifes:
        box(ax, x - 1.55, 6.55, 3.1, 0.62, t, fs=8.2)
        ax.plot([x, x], [6.52, 0.95], color=GREY, lw=0.9, ls=(0, (4, 3)), zorder=2)

    ax.add_patch(Rectangle((5.40, 1.85), 0.30, 4.20, fc=LIGHT, ec=BLUE, lw=0.9,
                           zorder=3))

    def msg(y, x1, x2, text, dashed=False):
        arrow(ax, (x1, y), (x2, y), style="-|>",
              ls=(0, (4, 3)) if dashed else "-", lw=1.0)
        label(ax, (x1 + x2) / 2, y + 0.22, text, fs=7.4, bold=False, color="#333333")

    msg(5.95, 2.05, 5.55, "generate(\"product\")")
    msg(5.35, 5.55, 9.05, "查询规则（enabled = 1）")
    msg(4.85, 9.05, 5.55, "返回 CodeRule", dashed=True)
    msg(4.20, 5.55, 12.05, "SELECT … FOR UPDATE")
    msg(3.65, 12.05, 5.55, "返回 curr_value", dashed=True)
    msg(3.05, 5.55, 12.05, "UPDATE curr_value + 1")
    msg(2.40, 5.55, 2.05, "CP20261115-0007", dashed=True)
    label(ax, 5.55, 1.55, "拼装：前缀 + 日期段 + 分隔符 + 补零流水", fs=7.2, bold=False,
          color=GREY)

    save(fig, "fig5-2_seq_code.png", ax, (0.30, 13.00, 0.80, 7.30), k=0.95)


# ------------------------------------------------------------------ 图 5-3 BOM 维护活动图
def fig5_3():
    W, H = 13.2, 9.4
    fig, ax = canvas(W, H)

    ax.add_patch(Ellipse((3.55, 8.85), 0.34, 0.34, fc=NAVY, ec=NAVY, zorder=3))
    steps = [
        (8.15, "打开产品表单"),
        (7.15, "填写名称 / 规格 / 状态"),
        (5.75, "维护 BOM 明细\n（增 / 改 / 删）"),
        (4.25, "保存（事务开始）"),
        (3.25, "写产品主表"),
        (2.25, "写 BOM 子表"),
        (1.25, "提交事务"),
    ]
    for y, t in steps:
        box(ax, 1.85, y - 0.38, 3.4, 0.78, t, fs=8.2)

    def diamond(cy, text):
        pts = [(3.55, cy + 0.62), (4.75, cy), (3.55, cy - 0.62), (2.35, cy)]
        ax.add_patch(plt.Polygon(pts, closed=True, fc=LIGHT2, ec=NAVY, lw=1.0, zorder=3))
        ax.text(3.55, cy, text, ha="center", va="center", fontsize=7.4, zorder=4,
                color="#222222", linespacing=1.4)

    for y1, y2 in ((8.82, 8.55), (7.77, 7.55), (6.77, 6.39), (5.13, 4.65),
                   (3.87, 3.65), (2.87, 2.65), (1.87, 1.65)):
        arrow(ax, (3.55, y1), (3.55, y2), style="-")

    diamond(5.75 + 0.0, "")
    # 决策点 1：名称规格是否合法
    diamond(6.95, "名称规格\n是否完整")
    label(ax, 3.95, 6.95, "", fs=7)

    ax.add_patch(Ellipse((3.55, 0.55), 0.42, 0.42, fc="white", ec=NAVY, lw=1.2,
                         zorder=3))
    ax.add_patch(Ellipse((3.55, 0.55), 0.26, 0.26, fc=NAVY, ec=NAVY, zorder=4))

    label(ax, 8.10, 6.95, "否：提示「产品名称不能为空」", fs=7.2, bold=False,
          color="#333333")
    arrow(ax, (4.78, 6.95), (7.30, 6.95), style="-")
    label(ax, 8.10, 5.30, "否：提示「用量必须大于 0」", fs=7.2, bold=False,
          color="#333333")

    save(fig, "fig5-3_activity.png", ax, (0.30, 12.60, 0.20, 9.20), k=0.95)


# ------------------------------------------------------------------ 图 5-4 工单状态图
def fig5_4():
    W, H = 12.6, 4.6
    fig, ax = canvas(W, H)

    ax.add_patch(Ellipse((0.85, 3.55), 0.30, 0.30, fc=NAVY, ec=NAVY, zorder=3))
    box(ax, 1.75, 3.05, 2.85, 0.95, "草稿\n(1)", fs=8.6)
    box(ax, 5.55, 3.05, 2.85, 0.95, "已下达\n(2)", fs=8.6, fill=LIGHT2, edge=BLUE,
        color="#222222")
    box(ax, 9.45, 3.05, 2.85, 0.95, "已完工\n(3)", fs=8.6, fill=LIGHT2, edge=BLUE,
        color="#222222")

    arrow(ax, (1.20, 3.55), (1.70, 3.55), style="-")
    arrow(ax, (4.62, 3.55), (5.52, 3.55), style="-|>")
    label(ax, 5.07, 3.80, "下达", fs=7.8, bold=False)
    arrow(ax, (8.42, 3.55), (9.42, 3.55), style="-|>")
    label(ax, 8.92, 3.80, "完工", fs=7.8, bold=False)
    arrow(ax, (7.00, 3.02), (4.20, 3.02), style="-|>", rad=0.55)
    label(ax, 5.55, 1.85, "撤回（未报完工前）", fs=7.4, bold=False)

    label(ax, 6.30, 4.38, "工单状态迁移", fs=8.4)

    save(fig, "fig5-4_state.png", ax, (0.40, 12.55, 1.30, 4.55), k=0.95)



# ------------------------------------------------------------------ 图 6-1 界面布局示意
def fig6_1():
    W, H = 13.4, 8.6
    fig, ax = canvas(W, H)

    def frame(x, y, w, h, title):
        ax.add_patch(Rectangle((x, y), w, h, fc="white", ec="#9AA5B4", lw=1.2,
                               zorder=2))
        ax.add_patch(Rectangle((x, y + h - 0.62), w, 0.62, fc="#EDF1F7", ec="#9AA5B4",
                               lw=1.2, zorder=3))
        ax.text(x + 0.18, y + h - 0.31, title, ha="left", va="center", fontsize=8.2,
                color=NAVY, fontweight="bold", zorder=4)

    def field(x, y, w, text, h=0.44, label=None, fs=7.2):
        if label:
            ax.text(x, y + h / 2, label, ha="left", va="center", fontsize=fs,
                    color="#333333", zorder=4)
            x += 1.05
            w -= 1.05
        ax.add_patch(Rectangle((x, y), w, h, fc="white", ec="#B9C2CF", lw=0.9,
                               zorder=3))
        ax.text(x + 0.12, y + h / 2, text, ha="left", va="center", fontsize=fs,
                color="#777777", zorder=4)

    def button(x, y, w, text, primary=False, h=0.44):
        ax.add_patch(Rectangle((x, y), w, h, fc=BLUE if primary else "white",
                               ec=BLUE, lw=0.9, zorder=3))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7.0,
                color="white" if primary else BLUE, zorder=4)

    # ---- 左：列表页
    frame(0.20, 0.90, 6.10, 7.50, "文创产品 · 列表")
    field(0.40, 7.10, 1.75, "产品名称")
    field(2.35, 7.10, 1.55, "产品编码")
    field(4.10, 7.10, 1.05, "状态")
    button(5.25, 7.10, 0.90, "查询", primary=True)

    button(0.40, 6.45, 0.95, "新增", primary=True)
    button(1.45, 6.45, 0.95, "删除")

    ax.add_patch(Rectangle((0.40, 5.85), 5.75, 0.45, fc="#E8EEF7", ec="#B9C2CF",
                           lw=0.9, zorder=3))
    heads = [(0.40, 1.85, "产品名称"), (2.30, 2.30, "产品编码"),
             (4.70, 1.40, "状态")]
    for x, w, t in heads:
        ax.text(x + 0.12, 6.07, t, ha="left", va="center", fontsize=7.0,
                color=NAVY, fontweight="bold", zorder=4)

    rows = [("校徽帆布包", "CP20261115-0001", "批量制作"),
            ("金属校徽", "CP20261115-0002", "已入库"),
            ("校园明信片", "CP20261115-0003", "打样中"),
            ("纪念马克杯", "CP20261115-0004", "设计中")]
    for i, r in enumerate(rows):
        y = 5.40 - i * 0.62
        ax.add_patch(Rectangle((0.40, y), 5.75, 0.55, fc="white", ec="#DCE2EA",
                               lw=0.8, zorder=3))
        for (x, w, _), val in zip(heads, r):
            ax.text(x + 0.12, y + 0.28, val, ha="left", va="center", fontsize=6.8,
                    color="#333333", zorder=4)

    for x in (2.30, 4.70):
        ax.plot([x, x], [5.40 - 3 * 0.62, 6.30], color="#DCE2EA", lw=0.8, zorder=4)

    ax.text(5.85, 1.05, "共 4 条  ‹ 1 ›", ha="right", va="center", fontsize=6.8,
            color="#555555", zorder=4)

    # ---- 右：表单页
    frame(6.70, 0.90, 6.10, 7.50, "文创产品 · 编辑")
    field(6.90, 7.05, 5.55, "校徽帆布包", label="产品名称：")
    field(6.90, 6.45, 5.55, "CP20261115-0001（自动生成）", label="产品编码：")
    field(6.90, 5.85, 5.55, "35×40cm 米白", label="规　　格：")
    field(6.90, 5.25, 5.55, "批量制作", label="产品状态：")

    ax.add_patch(Rectangle((6.90, 4.58), 1.60, 0.44, fc="white", ec=BLUE, lw=1.0,
                           zorder=3))
    ax.text(7.70, 4.80, "基本信息", ha="center", va="center", fontsize=7.0,
            color=BLUE, fontweight="bold", zorder=4)
    ax.text(9.32, 4.80, "BOM 清单（3）", ha="center", va="center", fontsize=7.0,
            color="#666666", zorder=4)
    ax.plot([6.90, 12.45], [4.58, 4.58], color="#C9D2DE", lw=1.0, zorder=3)
    ax.add_patch(plt.Polygon([(11.95, 5.60), (12.15, 5.60), (12.05, 5.42)],
                             closed=True, fc="#777777", ec="none", zorder=4))

    ax.add_patch(Rectangle((6.90, 4.02), 5.55, 0.42, fc="#E8EEF7", ec="#B9C2CF",
                           lw=0.9, zorder=3))
    for x, t in [(7.02, "物料"), (8.90, "用量"), (9.90, "单位"), (10.90, "操作")]:
        ax.text(x, 4.23, t, ha="left", va="center", fontsize=7.0, color=NAVY,
                fontweight="bold", zorder=4)
    bom = [("12 安帆布", "0.6", "米"), ("涤纶线", "1", "卷"), ("织唛标签", "1", "个")]
    for i, r in enumerate(bom):
        y = 3.50 - i * 0.50
        ax.add_patch(Rectangle((6.90, y), 5.55, 0.44, fc="white", ec="#DCE2EA",
                               lw=0.8, zorder=3))
        for x, val in zip((7.02, 8.90, 9.90), r):
            ax.text(x, y + 0.22, val, ha="left", va="center", fontsize=6.8,
                    color="#333333", zorder=4)
        ax.text(10.92, y + 0.22, "删除", ha="left", va="center", fontsize=6.6,
                color=BLUE, zorder=4)

    button(6.90, 1.95, 1.30, "+ 添加行")
    button(10.55, 1.15, 0.85, "取消")
    button(11.50, 1.15, 0.95, "保存", primary=True)

    label(ax, 3.25, 8.62, "（a）列表页", fs=8.0, bold=False, color=GREY)
    label(ax, 9.75, 8.62, "（b）表单页与 BOM 标签页", fs=8.0, bold=False, color=GREY)

    save(fig, "fig6-1_ui.png", ax, (0.05, 13.35, 0.80, 8.85), k=0.96)



def fig6_3():
    import matplotlib.patches as mpatches
    fig, ax = canvas(13.4, 8.8)
    ax.set_xlim(0, 13.4)
    ax.set_ylim(0, 8.8)
    ax.axis("off")

    def panel(top, sql, header, rows, widths):
        n = len(rows)
        h = 0.62 + 0.34 * n
        ax.text(0.40, top + 0.10, sql, fontsize=7.2, color=NAVY, ha="left", va="bottom")
        box = mpatches.Rectangle((0.40, top - h), 12.6, h, facecolor="#F4F7FC",
                                 edgecolor=NAVY, linewidth=0.7, zorder=1)
        ax.add_patch(box)
        x = 0.62
        for w, hd in zip(widths, header):
            ax.text(x, top - 0.28, hd, fontsize=6.6, color=NAVY, ha="left", va="center",
                    fontweight="bold", zorder=3)
            x += w
        ax.plot([0.52, 12.88], [top - 0.44, top - 0.44], color=NAVY, linewidth=0.6, zorder=3)
        for i, r in enumerate(rows):
            y = top - 0.62 - 0.17 - 0.34 * i
            x = 0.62
            for w, v in zip(widths, r):
                ax.text(x, y, v, fontsize=6.8, color="#2B2B2B", ha="left", va="center", zorder=3)
                x += w
        return top - h

    y = panel(8.55, "mysql> select code, name, spec from cw_product order by code limit 5;",
              ["code", "name", "spec"],
              [["CP20261115-0025", "校徽帆布包", "35x40cm"],
               ["CP20261115-0026", "金属校徽", "直径 3cm"],
               ["CP20261115-0117", "测试重复BOM", "—"],
               ["CP20261115-0118", "校徽帆布包", "35x40cm"]],
              [3.9, 4.3, 4.2])

    y = panel(y - 0.62, "mysql> select rule_code, date_seg, curr_value from cw_code_seq;",
              ["rule_code", "date_seg", "curr_value"],
              [["CP", "20261115", "143"],
               ["MT", "20261115", "15"],
               ["WO", "20261115", "6"]],
              [3.9, 4.3, 4.2])

    panel(y - 0.62, "mysql> select count(*) from cw_product / cw_material / cw_product_bom ...",
          ["表", "行数"],
          [["cw_product / cw_material", "7 / 15"],
           ["cw_product_bom / cw_work_order", "14 / 6"]],
          [8.4, 4.0])

    save(fig, "fig6-3_db.png", ax, (0.1, 13.3, 2.28, 8.72), k=1.0)


def main():
    fig2_1()
    fig4_1()
    fig4_2()
    fig4_3()
    fig4_4()
    fig5_1()
    fig5_2()
    fig5_3()
    fig5_4()
    fig6_1()
    fig6_3()


if __name__ == "__main__":
    main()
