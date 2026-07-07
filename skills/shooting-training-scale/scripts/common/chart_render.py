# -*- coding: utf-8 -*-
"""训练评估图表渲染模块。

提供射击训练评估中常用的图表生成功能，包括：
- 五维度雷达图
- 团队配置对比柱状图
- 月度进度折线图

依赖 matplotlib 和 numpy。若未安装，所有渲染函数返回 None 并打印警告。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# 可选依赖检查
# ---------------------------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")  # 无头模式，不弹出窗口
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    import numpy as np

    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False
    plt = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------

# 当前文件所在目录（common/）
_CURRENT_DIR: Path = Path(__file__).parent.resolve()

# shooting-training-scale 根目录
_SCALE_ROOT: Path = _CURRENT_DIR.parent.parent

# 图表默认输出目录
_DIAGRAMS_DIR: Path = _SCALE_ROOT / "assets" / "diagrams"

# 省赛达标线常量
_PROVINCIAL_STANDARD = 350  # 省赛达标线总分


# ---------------------------------------------------------------------------
# 内部：中文字体配置
# ---------------------------------------------------------------------------

def _setup_chinese_font() -> Optional[Any]:
    """配置 matplotlib 中文字体。

    依次尝试 SimHei、Microsoft YaHei 等常见中文字体。
    若均不可用，回退到系统默认字体。

    Returns:
        字体属性对象（FontProperties），若 matplotlib 不可用则返回 None。
    """
    if not _HAS_MATPLOTLIB:
        return None

    # 候选中文字体列表（Windows 优先）
    chinese_fonts = [
        "SimHei",
        "Microsoft YaHei",
        "WenQuanYi Micro Hei",
        "Noto Sans CJK SC",
        "PingFang SC",
        "STHeiti",
        "Arial Unicode MS",
    ]

    available_fonts = {f.name for f in fm.fontManager.ttflist}

    for font_name in chinese_fonts:
        if font_name in available_fonts:
            return fm.FontProperties(family=font_name)

    # 回退：使用默认字体并打印警告
    print("[警告] 未找到中文字体，图表中文可能显示为方块。请安装 SimHei 或 Microsoft YaHei 字体。")
    return fm.FontProperties()  # 使用默认


def _ensure_output_dir(output_path: Optional[str] = None) -> Path:
    """确保输出目录存在，返回最终的输出文件路径。

    Args:
        output_path: 用户指定的输出路径。若为 None，使用默认 diagrams 目录。

    Returns:
        确认目录存在后的输出路径对象。
    """
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    else:
        _DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
        return _DIAGRAMS_DIR


# ---------------------------------------------------------------------------
# 公开 API：雷达图
# ---------------------------------------------------------------------------

def render_radar_chart(
    scores: Dict[str, float],
    title: str = "射击训练五维度评估",
    output_path: Optional[str] = None,
) -> Optional[str]:
    """生成五维度雷达图。

    Args:
        scores: 五维度得分字典，格式如
                {"空枪基础定型": 85, "实弹射击实操": 72, ...}。
                每个维度的值为 0~100 的得分。
        title: 图表标题。
        output_path: 输出图片文件路径（如 "radar.png"）。
                    若为 None，保存到 assets/diagrams/ 下自动命名。

    Returns:
        生成的图片文件路径字符串。若 matplotlib 不可用则返回 None。
    """
    if not _HAS_MATPLOTLIB:
        print("[警告] matplotlib 未安装，无法生成雷达图。请执行: pip install matplotlib")
        return None

    font_prop = _setup_chinese_font()

    # 准备数据
    labels = list(scores.keys())
    values = [scores.get(k, 0) for k in labels]
    n = len(labels)

    if n == 0:
        print("[警告] 得分数据为空，无法生成雷达图。")
        return None

    # 计算角度（闭合多边形）
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    values_closed = values + [values[0]]
    angles_closed = angles + [angles[0]]

    # 创建极坐标图
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    fig.patch.set_facecolor("white")

    # 绘制填充区域
    ax.fill(angles_closed, values_closed, color="#4A90D9", alpha=0.25)
    ax.plot(angles_closed, values_closed, color="#1A3A6B", linewidth=2, marker="o", markersize=6)

    # 设置刻度标签
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontproperties=font_prop, fontsize=12)

    # 设置径向刻度
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=9)

    # 在各维度标注得分数字
    for angle, value, label in zip(angles, values, labels):
        # 在数据点外侧偏移标注
        offset = 8
        ax.annotate(
            f"{value}",
            xy=(angle, value),
            xytext=(angle, value + offset),
            textcoords="data",
            ha="center",
            va="bottom",
            fontsize=13,
            fontweight="bold",
            color="#1A3A6B",
            fontproperties=font_prop,
        )

    # 设置标题
    ax.set_title(title, fontproperties=font_prop, fontsize=16, fontweight="bold", pad=20)

    # 确定输出路径
    if output_path is None:
        _DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
        out_file = _DIAGRAMS_DIR / "radar_chart.png"
    else:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(str(out_file), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    return str(out_file)


# ---------------------------------------------------------------------------
# 公开 API：团队配置对比柱状图
# ---------------------------------------------------------------------------

def render_team_comparison(
    current_team: Dict[str, int],
    standard_team: Dict[str, int],
    output_path: Optional[str] = None,
) -> Optional[str]:
    """生成团队配置水平对比柱状图。

    Args:
        current_team: 当前团队岗位配置，格式如 {"主教练": 1, "助理教练": 3, ...}。
        standard_team: 标准团队岗位配置，格式同上。
        output_path: 输出图片文件路径。若为 None，使用默认路径。

    Returns:
        生成的图片文件路径字符串。若 matplotlib 不可用则返回 None。
    """
    if not _HAS_MATPLOTLIB:
        print("[警告] matplotlib 未安装，无法生成对比图。请执行: pip install matplotlib")
        return None

    font_prop = _setup_chinese_font()

    # 合并所有岗位
    all_positions = list(dict.fromkeys(list(current_team.keys()) + list(standard_team.keys())))
    n = len(all_positions)

    if n == 0:
        print("[警告] 团队数据为空，无法生成对比图。")
        return None

    current_vals = [current_team.get(pos, 0) for pos in all_positions]
    standard_vals = [standard_team.get(pos, 0) for pos in all_positions]

    # 根据是否满足标准确定颜色
    bar_colors = []
    for i, pos in enumerate(all_positions):
        if current_vals[i] < standard_vals[i]:
            bar_colors.append("#E74C3C")  # 红色 - 缺失
        else:
            bar_colors.append("#27AE60")  # 绿色 - 满足

    # 创建水平柱状图
    fig, ax = plt.subplots(figsize=(10, max(4, n * 0.6)))
    fig.patch.set_facecolor("white")

    y_pos = np.arange(n)
    bar_height = 0.35

    # 当前配置柱
    bars1 = ax.barh(
        y_pos + bar_height / 2,
        current_vals,
        bar_height,
        label="当前配置",
        color=bar_colors,
        edgecolor="white",
        linewidth=0.5,
    )

    # 标准配置柱
    bars2 = ax.barh(
        y_pos - bar_height / 2,
        standard_vals,
        bar_height,
        label="标准配置",
        color="#3498DB",
        edgecolor="white",
        linewidth=0.5,
    )

    # 标注数值
    for bar in bars1:
        width = bar.get_width()
        ax.text(
            width + 0.1,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)}",
            va="center",
            ha="left",
            fontsize=11,
            fontweight="bold",
        )

    for bar in bars2:
        width = bar.get_width()
        ax.text(
            width + 0.1,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)}",
            va="center",
            ha="left",
            fontsize=11,
            color="#3498DB",
        )

    # 设置轴
    ax.set_yticks(y_pos)
    ax.set_yticklabels(all_positions, fontproperties=font_prop, fontsize=12)
    ax.set_xlabel("人数", fontproperties=font_prop, fontsize=12)
    ax.set_title("团队岗位配置对比", fontproperties=font_prop, fontsize=16, fontweight="bold")
    ax.legend(loc="lower right", prop=font_prop)

    ax.set_xlim(0, max(max(current_vals), max(standard_vals)) + 1.5)

    plt.tight_layout()

    # 确定输出路径
    if output_path is None:
        _DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
        out_file = _DIAGRAMS_DIR / "team_comparison.png"
    else:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(str(out_file), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    return str(out_file)


# ---------------------------------------------------------------------------
# 公开 API：月度进度折线图
# ---------------------------------------------------------------------------

def render_progress_line(
    monthly_data: List[Dict[str, Any]],
    output_path: Optional[str] = None,
) -> Optional[str]:
    """生成月度训练进度折线图。

    Args:
        monthly_data: 月度数据列表，每项为字典，包含：
                     - "month": 月份字符串，如 "2026-01"
                     - "total_score": 当月总分
        output_path: 输出图片文件路径。若为 None，使用默认路径。

    Returns:
        生成的图片文件路径字符串。若 matplotlib 不可用则返回 None。
    """
    if not _HAS_MATPLOTLIB:
        print("[警告] matplotlib 未安装，无法生成折线图。请执行: pip install matplotlib")
        return None

    font_prop = _setup_chinese_font()

    if not monthly_data:
        print("[警告] 月度数据为空，无法生成折线图。")
        return None

    # 提取数据
    months = [item.get("month", "") for item in monthly_data]
    scores = [float(item.get("total_score", 0)) for item in monthly_data]

    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("white")

    # 绘制折线
    x_pos = np.arange(len(months))
    ax.plot(x_pos, scores, color="#2980B9", linewidth=2.5, marker="o", markersize=8,
            markerfacecolor="#3498DB", markeredgecolor="white", markeredgewidth=2)

    # 填充折线下方区域
    ax.fill_between(x_pos, scores, alpha=0.15, color="#3498DB")

    # 标注省赛达标线
    ax.axhline(
        y=_PROVINCIAL_STANDARD,
        color="#E74C3C",
        linestyle="--",
        linewidth=1.5,
        label=f"省赛达标线 ({_PROVINCIAL_STANDARD})",
    )

    # 标注各月分数
    for i, (x, score) in enumerate(zip(x_pos, scores)):
        offset = 8 if score >= _PROVINCIAL_STANDARD else -15
        va = "bottom" if score >= _PROVINCIAL_STANDARD else "top"
        ax.annotate(
            f"{int(score)}",
            xy=(x, score),
            xytext=(0, offset),
            textcoords="offset points",
            ha="center",
            va=va,
            fontsize=11,
            fontweight="bold",
            color="#2C3E50",
        )

    # 设置轴
    ax.set_xticks(x_pos)
    ax.set_xticklabels(months, rotation=30, ha="right", fontproperties=font_prop, fontsize=10)
    ax.set_ylabel("总分", fontproperties=font_prop, fontsize=12)
    ax.set_xlabel("月份", fontproperties=font_prop, fontsize=12)
    ax.set_title("月度训练进度追踪", fontproperties=font_prop, fontsize=16, fontweight="bold")
    ax.legend(prop=font_prop, fontsize=11)

    # Y轴范围
    y_min = min(min(scores), _PROVINCIAL_STANDARD) - 30
    y_max = max(scores) + 30
    ax.set_ylim(y_min, y_max)

    # 网格
    ax.grid(True, alpha=0.3, linestyle="-")
    ax.set_axisbelow(True)

    plt.tight_layout()

    # 确定输出路径
    if output_path is None:
        _DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
        out_file = _DIAGRAMS_DIR / "progress_line.png"
    else:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(str(out_file), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    return str(out_file)


# ---------------------------------------------------------------------------
# 测试入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("chart_render.py 模块测试")
    print("=" * 60)

    if not _HAS_MATPLOTLIB:
        print("\n[警告] matplotlib 未安装，跳过所有图表渲染测试。")
        print("    安装命令: pip install matplotlib numpy")
    else:
        # 1. 雷达图测试
        print("\n[1] render_radar_chart 测试")
        scores = {
            "空枪基础定型": 85,
            "实弹射击实操": 72,
            "体能储备": 68,
            "心理素质": 80,
            "战术素养": 75,
        }
        radar_path = render_radar_chart(scores)
        print(f"    雷达图已保存: {radar_path}")

        # 2. 团队对比图测试
        print("\n[2] render_team_comparison 测试")
        current = {"主教练": 1, "助理教练": 2, "体能教练": 1, "心理辅导": 0}
        standard = {"主教练": 1, "助理教练": 3, "体能教练": 1, "心理辅导": 1, "队医": 1}
        compare_path = render_team_comparison(current, standard)
        print(f"    对比图已保存: {compare_path}")

        # 3. 月度进度折线图测试
        print("\n[3] render_progress_line 测试")
        monthly = [
            {"month": "2026-01", "total_score": 280},
            {"month": "2026-02", "total_score": 310},
            {"month": "2026-03", "total_score": 330},
            {"month": "2026-04", "total_score": 355},
            {"month": "2026-05", "total_score": 370},
            {"month": "2026-06", "total_score": 390},
        ]
        line_path = render_progress_line(monthly)
        print(f"    折线图已保存: {line_path}")

        print(f"\n    图表输出目录: {_DIAGRAMS_DIR}")

    print("\n" + "=" * 60)
    print("所有测试完成")
    print("=" * 60)
