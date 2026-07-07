# -*- coding: utf-8 -*-
"""报告导出层统一入口 - Orchestrator-Agent

聚合所有业务计算模块（量表评分、身体机能、团队审计、训练统计、文献匹配），
生成结构化报告数据，并支持 Markdown / JSON / TXT 三种格式导出。

顶层入口：generate_full_report()
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any

# 确保能导入同层脚本
sys.path.insert(0, str(Path(__file__).parent))

# ---------- 业务模块导入 ----------
from score_calc import calc_score
from body_index_check import check_index
from team_audit import audit_team
from data_stat import monthly_stats

# 以下模块可能尚未创建，采用 try/except 以保证脚本可独立运行
try:
    from common.file_io import get_assets_dir, save_json, load_reference_index
except ImportError:
    get_assets_dir = None
    save_json = None
    load_reference_index = None

try:
    from common.math_calc import classify_level
except ImportError:
    classify_level = None

try:
    from literature_match import get_all_modules_papers
except ImportError:
    get_all_modules_papers = None


# ======================== 中文名 → 英文键映射 ========================

# 五维度量表中文名 → score_calc 使用的英文键
DIM_NAME_MAP: dict[str, str] = {
    "空枪基础定型": "aimless_foundation",
    "实弹射击实操": "live_fire",
    "射击专项体能": "physical_fitness",
    "赛场高压心理": "mental_resilience",
    "装备适配能力": "equipment_fitting",
}

# 身体指标中文名 → body_index_check 使用的英文键
BODY_NAME_MAP: dict[str, str] = {
    "静息心率": "resting_hr",
    "闭眼单脚站立": "single_leg_stance",
    "静力托举": "static_hold",
    "肩宽cm": "shoulder_width",
    "臂展cm": "wingspan",
    "平板支撑": "plank_hold",
    "弹壳叠放": "shell_stack",
    "扣机精度": "trigger_precision",
}

# 团队岗位中文名 → 英文键
ROLE_NAME_MAP: dict[str, str] = {
    "主教练": "head_coach",
    "助理教练": "assistant_coach",
    "体能教练": "fitness_coach",
    "心理辅导师": "psychologist",
    "队医": "team_doctor",
    "枪械师": "armorer",
    "营养师": "nutritionist",
    "数据分析师": "data_analyst",
}

# 反向映射：英文键 → 中文名（用于报告展示）
ROLE_LABEL_MAP: dict[str, str] = {v: k for k, v in ROLE_NAME_MAP.items()}


# ======================== 工具函数 ========================

def _translate_scores(scores: dict) -> dict:
    """将中文维度键转换为 score_calc 所需的英文键。

    Args:
        scores: 中文维度键的得分字典，如 {"空枪基础定型": 85, ...}

    Returns:
        英文键的得分字典，如 {"aimless_foundation": 85, ...}
    """
    translated: dict[str, int | float] = {}
    for cn_name, value in scores.items():
        en_key = DIM_NAME_MAP.get(cn_name)
        if en_key is not None:
            translated[en_key] = value
        else:
            # 未知键直接透传
            translated[cn_name] = value
    return translated


def _translate_body(body_data: dict) -> dict:
    """将中文身体指标键转换为 body_index_check 所需的英文键。

    Args:
        body_data: 中文指标键的数据字典

    Returns:
        英文键的数据字典
    """
    translated: dict[str, Any] = {}
    for cn_name, value in body_data.items():
        en_key = BODY_NAME_MAP.get(cn_name)
        if en_key is not None:
            translated[en_key] = value
        else:
            translated[cn_name] = value
    return translated


def _ensure_output_dir(output_dir: str | None) -> str:
    """确保输出目录存在，不存在则自动创建。

    Args:
        output_dir: 输出目录路径。为 None 时使用默认路径。

    Returns:
        确认存在的输出目录绝对路径。
    """
    if output_dir is None:
        # 默认输出到 scripts/assets/reports/
        output_dir = str(Path(__file__).parent / "assets" / "reports")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return str(output_path.resolve())


def _build_timestamp() -> str:
    """生成当前时间的格式化时间戳。

    Returns:
        格式为 YYYYMMDD_HHMMSS 的时间戳字符串。
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _get_level_label(level: str | None) -> str:
    """根据综合得分率返回等级标签。

    Args:
        level: 来自 calc_score 的等级字符串，如 "国家队"。

    Returns:
        可读的等级标签字符串。
    """
    if level:
        return str(level)
    return "未评级"


# ======================== 聚合业务计算 ========================

def _aggregate_report_data(
    scores: dict,
    body_data: dict,
    team: list,
    team_type: str,
    records: list | None,
) -> dict:
    """聚合所有业务模块的计算结果，构建结构化报告数据。

    Args:
        scores: 五维度中文得分字典。
        body_data: 身体指标数据字典。
        team: 当前团队岗位列表。
        team_type: 团队类型标识。
        records: 训练记录列表（可选）。

    Returns:
        包含所有聚合结果的字典，可直接用于各格式导出。
    """
    # 1. 量表评分
    en_scores = _translate_scores(scores)
    score_result: dict = calc_score(en_scores)

    # 2. 身体机能评估
    en_body = _translate_body(body_data)
    body_result: dict = check_index(en_body)

    # 3. 团队审计
    team_result: dict = audit_team(team, team_type)

    # 4. 训练统计（可选）
    training_stats: dict | None = None
    if records:
        # 从记录中提取年月，汇总统计
        try:
            all_stats = _compute_training_summary(records)
            training_stats = all_stats
        except Exception as e:
            training_stats = {"error": f"训练统计计算失败: {e}"}

    # 5. 参考文献列表
    literature: list = []
    if get_all_modules_papers is not None:
        try:
            literature = get_all_modules_papers()
        except Exception as e:
            literature = [{"error": f"文献匹配失败: {e}"}]

    # 6. 等级判定（如有 classify_level 则使用，否则沿用 score_calc 结果）
    final_level = score_result.get("level", "未评级")
    if classify_level is not None:
        try:
            final_level = classify_level(score_result)
        except Exception:
            pass

    # 组装报告数据
    report_data: dict = {
        "meta": {
            "生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "报告类型": "射击运动员综合训练能力评估报告",
        },
        "个人训练水平": {
            "综合评级": final_level,
            "总分": score_result.get("total", 0),
            "满分": score_result.get("max_total", 0),
            "得分率": score_result.get("percentage", 0),
            "各维度得分": _build_cn_breakdown(score_result.get("breakdown", {})),
            "短板维度": score_result.get("weaknesses", []),
        },
        "身体机能评估": body_result,
        "保障团队审计": {
            "团队类型": team_result.get("team_type", "未知"),
            "完备度得分": team_result.get("score", 0),
            "完备度满分": team_result.get("max_score", 0),
            "完备度": team_result.get("percentage", 0),
            "评级": team_result.get("rating", "未评级"),
            "缺失岗位": team_result.get("missing_roles", []),
        },
        "训练统计": training_stats,
        "参考文献": literature,
    }
    return report_data


def _build_cn_breakdown(breakdown: dict) -> dict:
    """将英文维度的 breakdown 转换为中文展示格式。

    Args:
        breakdown: score_calc 返回的英文维度 breakdown 字典。

    Returns:
        中文维度的得分明细字典。
    """
    # 反向映射：英文键 → 中文名
    en_to_cn = {v: k for k, v in DIM_NAME_MAP.items()}
    cn_breakdown: dict[str, dict] = {}
    for en_key, info in breakdown.items():
        cn_name = en_to_cn.get(en_key, en_key)
        cn_breakdown[cn_name] = {
            "得分": info.get("score", 0),
            "满分": info.get("max", 0),
            "得分率": round(info.get("score", 0) / max(info.get("max", 1), 1) * 100, 1),
        }
    return cn_breakdown


def _compute_training_summary(records: list) -> dict:
    """从训练记录列表中汇总统计数据。

    当 records 非空时，尝试提取每条记录的年月并调用 monthly_stats，
    再汇总为整体概览。

    Args:
        records: 训练记录字典列表。

    Returns:
        汇总统计字典。
    """
    if not records:
        return {"总记录数": 0, "提示": "无训练记录"}

    summary: dict[str, Any] = {
        "总记录数": len(records),
        "月度统计": [],
        "汇总": {
            "总实弹发数": 0,
            "总空扣扳机次数": 0,
            "总定型保持时长_分钟": 0.0,
            "总训练时长_分钟": 0.0,
        },
    }

    # 按年月分组
    year_month_set: set[tuple[int, int]] = set()
    for r in records:
        date_str = r.get("日期", "")
        if "-" in date_str:
            parts = date_str.split("-")
            try:
                y, m = int(parts[0]), int(parts[1])
                year_month_set.add((y, m))
            except (ValueError, IndexError):
                continue

    for y, m in sorted(year_month_set):
        try:
            ms = monthly_stats(records, y, m)
            summary["月度统计"].append(ms)
            summary["汇总"]["总实弹发数"] += ms.get("total_live_rounds", 0)
            summary["汇总"]["总空扣扳机次数"] += ms.get("total_empty_trigger", 0)
            summary["汇总"]["总定型保持时长_分钟"] += ms.get("total_hold_min", 0)
            summary["汇总"]["总训练时长_分钟"] += ms.get("total_train_min", 0)
        except Exception:
            continue

    return summary


# ======================== 多格式导出函数 ========================

def export_markdown(report_data: dict, output_path: str) -> str:
    """将报告数据导出为 Markdown 格式文件。

    按照评估报告模板的八章结构生成：
    测评说明 → 基础信息 → 身体机能 → 五维评分 → 团队审计 → 提升方案 → 综合判定 → 参考文献

    Args:
        report_data: 由 _aggregate_report_data 生成的结构化数据。
        output_path: Markdown 文件的完整输出路径。

    Returns:
        生成的 Markdown 文本内容。
    """
    level_info = report_data.get("个人训练水平", {})
    body_info = report_data.get("身体机能评估", {})
    team_info = report_data.get("保障团队审计", {})
    train_info = report_data.get("训练统计")
    refs = report_data.get("参考文献", [])
    meta = report_data.get("meta", {})

    lines: list[str] = []

    # ---------- 标题 ----------
    lines.append("# 射击运动员综合训练能力评估报告\n")

    # ---------- 一、测评说明 ----------
    lines.append("## 一、测评说明\n")
    lines.append(f"- 报告生成时间：{meta.get('生成时间', '未知')}")
    lines.append("- 本报告基于射击运动员五维训练能力量表，对身体机能指标、实操训练量化评分、")
    lines.append("  保障团队架构完备度进行综合评估，并给出专项提升训练实施方案建议。")
    lines.append("- 评分标准对标国家队/国青队/省队/零基础四级体系。")
    lines.append("")

    # ---------- 二、受试者基础信息 ----------
    lines.append("## 二、受试者基础信息\n")
    lines.append("| 项目 | 信息 |")
    lines.append("|------|------|")
    lines.append("| 综合评级 | {} |".format(level_info.get("综合评级", "未评级")))
    lines.append("| 总分 | {}/{} |".format(level_info.get("总分", 0), level_info.get("满分", 0)))
    lines.append("| 得分率 | {}% |".format(level_info.get("得分率", 0)))
    lines.append("| 保障团队完备度 | {}% |".format(team_info.get("完备度", 0)))
    lines.append("| 团队审计评级 | {} |".format(team_info.get("评级", "未评级")))
    lines.append("")

    # ---------- 三、身体机能指标测评结果 ----------
    lines.append("## 三、身体机能指标测评结果\n")
    lines.append("| 指标 | 测量值 | 单位 | 达标等级 |")
    lines.append("|------|--------|------|----------|")

    # 将英文键转为中文展示
    en_to_cn_body = {v: k for k, v in BODY_NAME_MAP.items()}
    for en_key, info in body_info.items():
        cn_name = en_to_cn_body.get(en_key, en_key)
        value = info.get("value", "未测量") if info.get("value") is not None else "未测量"
        unit = info.get("unit", "")
        status = info.get("status", "未达标")
        lines.append("| {} | {} | {} | {} |".format(cn_name, value, unit, status))
    lines.append("")

    # ---------- 四、实操训练五大维度量化评分 ----------
    lines.append("## 四、实操训练五大维度量化评分\n")
    lines.append("| 维度 | 得分 | 满分 | 得分率 |")
    lines.append("|------|------|------|--------|")
    breakdown = level_info.get("各维度得分", {})
    for dim_name, dim_info in breakdown.items():
        lines.append("| {} | {} | {} | {}% |".format(
            dim_name,
            dim_info.get("得分", 0),
            dim_info.get("满分", 0),
            dim_info.get("得分率", 0),
        ))
    lines.append("")

    weaknesses = level_info.get("短板维度", [])
    if weaknesses:
        # 将短板维度的英文键转为中文
        en_to_cn_dim = {v: k for k, v in DIM_NAME_MAP.items()}
        cn_weaknesses = [en_to_cn_dim.get(w, w) for w in weaknesses]
        lines.append("**短板维度**：{}".format("、".join(cn_weaknesses)))
        lines.append("")

    # ---------- 五、保障团队架构完备度审计 ----------
    lines.append("## 五、保障团队架构完备度审计\n")
    lines.append("- **团队类型**：{}".format(team_info.get("团队类型", "未知")))
    lines.append("- **完备度**：{}/{}（{}%）".format(
        team_info.get("完备度得分", 0),
        team_info.get("完备度满分", 0),
        team_info.get("完备度", 0),
    ))
    lines.append("- **评级**：{}".format(team_info.get("评级", "未评级")))
    missing = team_info.get("缺失岗位", [])
    if missing:
        lines.append("- **缺失岗位**：{}".format("、".join(missing)))
    else:
        lines.append("- **缺失岗位**：无（配置完整）")
    lines.append("")

    # ---------- 六、专项提升训练实施方案 ----------
    lines.append("## 六、专项提升训练实施方案\n")
    if weaknesses:
        en_to_cn_dim = {v: k for k, v in DIM_NAME_MAP.items()}
        cn_weaknesses = [en_to_cn_dim.get(w, w) for w in weaknesses]
        lines.append("### 针对短板维度的提升建议\n")
        improvement_map: dict[str, str] = {
            "空枪基础定型": (
                "1. 每日空扣扳机次数提升至200次以上，分3组完成\n"
                "2. 每日定型保持时长逐步增加至15分钟\n"
                "3. 增加弹壳叠放练习，目标叠放3枚以上\n"
                "4. 呼吸控制训练：每日闭气练习，目标8秒以上"
            ),
            "实弹射击实操": (
                "1. 每日实弹训练量维持60发，注重10环集中度\n"
                "2. 弹着点密集度训练，目标散布小于25mm\n"
                "3. 增加模拟比赛场景的实弹训练\n"
                "4. 强化据枪一致性，每组10发射击"
            ),
            "射击专项体能": (
                "1. 平板支撑训练：目标90秒以上\n"
                "2. 侧平板支撑：目标60秒以上\n"
                "3. 静力托举：目标8分钟以上\n"
                "4. 闭眼单脚站立平衡训练：目标60秒以上"
            ),
            "赛场高压心理": (
                "1. 模拟比赛环境训练，逐步增加压力源\n"
                "2. 想象训练法：每日10分钟比赛场景可视化\n"
                "3. 建立个人赛前仪式流程并严格执行\n"
                "4. 心理抗压能力专项训练，目标压力下保持80%水平"
            ),
            "装备适配能力": (
                "1. 扣机引力一致性调试，目标偏差小于20g\n"
                "2. 枪托贴合度调整与适配\n"
                "3. 射击服合身度检查与调整\n"
                "4. 定期装备维护保养习惯培养"
            ),
        }
        for weak in cn_weaknesses:
            advice = improvement_map.get(weak, "- 暂无针对该维度的具体建议，需教练组评估后制定个性化方案。")
            lines.append("#### {}\n".format(weak))
            lines.append(advice)
            lines.append("")
    else:
        lines.append("当前各维度得分较为均衡，无明显短板。建议继续保持现有训练强度，")
        lines.append("并针对综合评级目标进行针对性强化训练。\n")

    # 团队补强建议
    if missing:
        lines.append("### 团队补强建议\n")
        lines.append("- 优先补充缺失岗位人员，提升保障团队完备度")
        lines.append("- 可考虑兼职或外聘方式弥补关键岗位空缺\n")
    lines.append("")

    # ---------- 七、参赛能力综合判定 ----------
    lines.append("## 七、参赛能力综合判定\n")
    final_level = level_info.get("综合评级", "未评级")
    pct = level_info.get("得分率", 0)
    team_pct = team_info.get("完备度", 0)

    lines.append("### 综合评级结果\n")
    lines.append("**选手等级：{}**（得分率：{}%）\n".format(final_level, pct))

    # 等级详细说明
    level_descriptions: dict[str, str] = {
        "国家队": "具备国家队选拔竞争力，建议参加全国锦标赛、全运会等高水平赛事。",
        "国青": "具备国青队选拔竞争力，建议参加全国青年锦标赛、青少年联赛等赛事。",
        "省赛": "具备省级赛事竞争力，建议参加省运会、省射击锦标赛等赛事。",
        "零基础合格": "已达到射击运动基础入门标准，建议持续训练并逐步提高。",
        "未评级": "尚未达到任何评级标准，建议从基础训练开始，循序渐进。"
    }
    desc = level_descriptions.get(final_level, level_descriptions["未评级"])
    lines.append("{}\n".format(desc))

    lines.append("### 综合评价\n")
    if pct >= 90 and team_pct >= 90:
        lines.append("选手个人能力和团队保障均处于优秀水平，具备参加国家级赛事的全面条件。")
    elif pct >= 70 and team_pct >= 70:
        lines.append("选手个人能力和团队保障均处于良好水平，具备参加省级及以上赛事的条件，")
        lines.append("建议针对短板维度进行专项强化。")
    elif pct >= 50 or team_pct >= 50:
        lines.append("选手个人能力或团队保障存在一定不足，建议重点补强短板，")
        lines.append("制定阶段性训练提升计划。")
    else:
        lines.append("选手个人能力和团队保障均有较大提升空间，建议从基础训练入手，")
        lines.append("逐步构建完整的训练保障体系。")
    lines.append("")

    # 训练统计摘要
    if train_info and isinstance(train_info, dict) and train_info.get("总记录数", 0) > 0:
        agg = train_info.get("汇总", {})
        lines.append("### 训练数据概览\n")
        lines.append("| 统计项 | 数值 |")
        lines.append("|--------|------|")
        lines.append("| 总记录数 | {} |".format(train_info.get("总记录数", 0)))
        lines.append("| 总实弹发数 | {} |".format(agg.get("总实弹发数", 0)))
        lines.append("| 总空扣扳机次数 | {} |".format(agg.get("总空扣扳机次数", 0)))
        lines.append("| 总定型保持时长(分钟) | {:.1f} |".format(agg.get("总定型保持时长_分钟", 0)))
        lines.append("| 总训练时长(分钟) | {:.1f} |".format(agg.get("总训练时长_分钟", 0)))
        lines.append("")

    # ---------- 八、参考文献列表 ----------
    lines.append("## 八、参考文献列表\n")
    if refs:
        for i, ref in enumerate(refs, 1):
            if isinstance(ref, dict):
                title = ref.get("title", ref.get("名称", str(ref)))
                author = ref.get("author", ref.get("作者", ""))
                if author:
                    lines.append("[{}] {}. {}\n".format(i, title, author))
                else:
                    lines.append("[{}] {}\n".format(i, title))
            else:
                lines.append("[{}] {}\n".format(i, ref))
    else:
        lines.append("暂无参考文献数据。\n")

    content = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return content


def export_json(report_data: dict, output_path: str) -> dict:
    """将报告数据导出为 JSON 格式文件。

    Args:
        report_data: 由 _aggregate_report_data 生成的结构化数据。
        output_path: JSON 文件的完整输出路径。

    Returns:
        写入的原始报告数据字典。
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    # 同时通过 common.file_io.save_json 备份（如可用）
    if save_json is not None:
        try:
            save_json(output_path, report_data)
        except Exception:
            pass

    return report_data


def export_txt(report_data: dict, output_path: str) -> str:
    """将报告数据导出为纯文本简报格式。

    纯文本格式去掉表格和 Markdown 语法，适合邮件正文或快速阅读。

    Args:
        report_data: 由 _aggregate_report_data 生成的结构化数据。
        output_path: TXT 文件的完整输出路径。

    Returns:
        生成的纯文本内容。
    """
    level_info = report_data.get("个人训练水平", {})
    team_info = report_data.get("保障团队审计", {})
    meta = report_data.get("meta", {})
    refs = report_data.get("参考文献", [])

    lines: list[str] = []
    sep = "=" * 60

    lines.append(sep)
    lines.append("  射击运动员综合训练能力评估报告（简报）")
    lines.append(sep)
    lines.append("生成时间：{}".format(meta.get("生成时间", "未知")))
    lines.append("")

    # 综合评级
    lines.append("-" * 40)
    lines.append("【综合评级】")
    lines.append("  等级：{}".format(level_info.get("综合评级", "未评级")))
    lines.append("  总分：{}/{}".format(level_info.get("总分", 0), level_info.get("满分", 0)))
    lines.append("  得分率：{}%".format(level_info.get("得分率", 0)))
    lines.append("")

    # 五维评分
    lines.append("【五维评分】")
    breakdown = level_info.get("各维度得分", {})
    for dim_name, dim_info in breakdown.items():
        lines.append("  {}：{}/{}（{}%）".format(
            dim_name,
            dim_info.get("得分", 0),
            dim_info.get("满分", 0),
            dim_info.get("得分率", 0),
        ))
    lines.append("")

    # 短板
    weaknesses = level_info.get("短板维度", [])
    if weaknesses:
        en_to_cn_dim = {v: k for k, v in DIM_NAME_MAP.items()}
        cn_weaknesses = [en_to_cn_dim.get(w, w) for w in weaknesses]
        lines.append("【短板维度】{}".format("、".join(cn_weaknesses)))
        lines.append("")

    # 团队审计
    lines.append("-" * 40)
    lines.append("【保障团队审计】")
    lines.append("  团队类型：{}".format(team_info.get("团队类型", "未知")))
    lines.append("  完备度：{}%".format(team_info.get("完备度", 0)))
    lines.append("  评级：{}".format(team_info.get("评级", "未评级")))
    missing = team_info.get("缺失岗位", [])
    if missing:
        lines.append("  缺失岗位：{}".format("、".join(missing)))
    lines.append("")

    # 参考文献
    if refs:
        lines.append("-" * 40)
        lines.append("【参考文献】")
        for i, ref in enumerate(refs, 1):
            if isinstance(ref, dict):
                title = ref.get("title", ref.get("名称", str(ref)))
                lines.append("  [{}] {}".format(i, title))
            else:
                lines.append("  [{}] {}".format(i, ref))
        lines.append("")

    lines.append(sep)
    lines.append("  报告结束")
    lines.append(sep)

    content = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return content


# ======================== 顶层入口函数 ========================

def generate_full_report(
    scores: dict,
    body_data: dict,
    team: list,
    team_type: str = "type_a_national",
    records: list | None = None,
    output_dir: str | None = None,
    formats: list[str] | None = None,
) -> dict:
    """报告导出层统一入口函数。

    聚合量表评分、身体机能评估、团队审计、训练统计、文献匹配等全部业务计算，
    根据指定格式生成评估报告文件。

    Args:
        scores: 五维度得分字典，中文键。如 {"空枪基础定型": 85, "实弹射击实操": 75, ...}
        body_data: 身体指标数据字典，中文键。如 {"静息心率": 58, "闭眼单脚站立": 52, ...}
        team: 当前团队岗位列表。如 ["head_coach", "assistant_coach", ...]
        team_type: 团队类型标识。默认 "type_a_national"。
        records: 训练记录列表（可选）。传入时将计算训练统计数据。
        output_dir: 输出目录路径（可选）。默认为 assets/reports/。
        formats: 输出格式列表（可选）。可选值 "markdown"、"json"、"txt"。
                 默认生成全部三种格式。

    Returns:
        结果字典，包含：
        - "report_data": 结构化报告数据
        - "files": 已生成的文件路径列表
        - "timestamp": 时间戳字符串

    Example::

        result = generate_full_report(
            scores={"空枪基础定型": 82, "实弹射击实操": 75},
            body_data={"静息心率": 58, "闭眼单脚站立": 52},
            team=["head_coach", "assistant_coach"],
        )
        print(result["files"])
    """
    if formats is None:
        formats = ["markdown", "json", "txt"]

    # 确保输出目录
    resolved_dir = _ensure_output_dir(output_dir)

    # 聚合业务数据
    report_data = _aggregate_report_data(scores, body_data, team, team_type, records)

    # 生成时间戳
    ts = _build_timestamp()
    base_name = "射击评估报告_{}".format(ts)

    # 按格式导出
    generated_files: list[str] = []
    exporters: dict[str, tuple] = {
        "markdown": (export_markdown, ".md"),
        "json": (export_json, ".json"),
        "txt": (export_txt, ".txt"),
    }

    for fmt in formats:
        if fmt not in exporters:
            print("[警告] 不支持的格式: {}，跳过。".format(fmt))
            continue
        export_func, ext = exporters[fmt]
        output_path = os.path.join(resolved_dir, "{}{}".format(base_name, ext))
        try:
            export_func(report_data, output_path)
            generated_files.append(output_path)
            print("[导出成功] {} -> {}".format(fmt, output_path))
        except Exception as e:
            print("[导出失败] {} -> {}（错误：{}）".format(fmt, output_path, e))

    return {
        "report_data": report_data,
        "files": generated_files,
        "timestamp": ts,
    }


# ======================== 演示调用 ========================

if __name__ == "__main__":
    print("=" * 60)
    print("  射击评估报告导出 - 统一入口演示")
    print("=" * 60)
    print()

    # 示例数据
    sample_scores: dict = {
        "空枪基础定型": 82,
        "实弹射击实操": 75,
        "射击专项体能": 68,
        "赛场高压心理": 71,
        "装备适配能力": 60,
    }

    sample_body_data: dict = {
        "静息心率": 58,
        "闭眼单脚站立": 52,
        "静力托举": 75,
        "肩宽cm": 38,
        "臂展cm": 175,
    }

    sample_team: list = [
        "head_coach",
        "assistant_coach",
        "fitness_coach",
        "psychologist",
        "team_doctor",
        "armorer",
    ]

    # 输出目录
    output_directory = str(Path(__file__).parent / "assets" / "reports")

    print("示例得分：{}".format(json.dumps(sample_scores, ensure_ascii=False)))
    print("身体指标：{}".format(json.dumps(sample_body_data, ensure_ascii=False)))
    print("团队岗位：{}".format(sample_team))
    print("输出目录：{}".format(output_directory))
    print()

    # 生成报告
    result = generate_full_report(
        scores=sample_scores,
        body_data=sample_body_data,
        team=sample_team,
        team_type="type_a_national",
        records=None,
        output_dir=output_directory,
        formats=["markdown", "json", "txt"],
    )

    print()
    print("-" * 60)
    print("生成完成！")
    print("时间戳：{}".format(result["timestamp"]))
    print("已生成文件：")
    for f in result["files"]:
        print("  - {}".format(f))
    print()
    print("综合评级：{}".format(
        result["report_data"]["个人训练水平"]["综合评级"]
    ))
    print("得分率：{}%".format(
        result["report_data"]["个人训练水平"]["得分率"]
    ))
    print("团队完备度：{}%".format(
        result["report_data"]["保障团队审计"]["完备度"]
    ))
