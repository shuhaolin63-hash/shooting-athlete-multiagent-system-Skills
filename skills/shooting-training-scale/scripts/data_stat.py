# -*- coding: utf-8 -*-
"""训练数据统计、弹药/时长汇总 - Data-Calc-Agent

支持月度统计、年度汇总、失误类型分析、进步曲线数据。
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

# 确保可以导入 common 工具层
sys.path.insert(0, str(Path(__file__).parent))

from common.file_io import get_assets_dir, load_csv
from common.math_calc import mean, sum_safe
from common.unit_convert import minutes_to_hours, rounds_to_string, training_volume_classify


def monthly_stats(records: list, year: int, month: int) -> dict:
    """
    月度训练数据统计汇总。

    Args:
        records: 训练记录列表（CSV 字典列表）
        year: 年份
        month: 月份

    Returns:
        月度统计结果
    """
    # 筛选当月记录
    monthly = [r for r in records if r.get("日期", "").startswith(f"{year}-{month:02d}")]

    # 使用 common 工具层统计
    total_live_rounds = sum_safe(monthly, key="实弹发数", cast=int)
    total_empty_trigger = sum_safe(monthly, key="空扣扳机次数", cast=int)
    total_hold_min = sum_safe(monthly, key="定型保持时长(分钟)", cast=float)
    total_train_min = sum_safe(monthly, key="训练总时长(分钟)", cast=float)

    # 平均心率
    hr_values = [int(r.get("静息心率(bpm)", 0) or 0) for r in monthly if r.get("静息心率(bpm)")]
    avg_hr_val = mean(hr_values)

    # 使用 common 工具层格式化
    total_hours = total_train_min / 60

    return {
        "year": year,
        "month": month,
        "total_days": len(monthly),
        "total_live_rounds": total_live_rounds,
        "total_live_rounds_formatted": rounds_to_string(total_live_rounds),
        "total_empty_trigger": total_empty_trigger,
        "total_hold_min": total_hold_min,
        "total_train_min": total_train_min,
        "total_train_hours_formatted": minutes_to_hours(total_train_min),
        "avg_resting_hr": avg_hr_val,
        "training_volume_level": training_volume_classify(total_live_rounds, total_hours),
    }


def annual_summary(records: list, year: int) -> dict:
    """
    年度训练数据汇总。

    Args:
        records: 训练记录列表（CSV 字典列表）
        year: 年份

    Returns:
        年度汇总 + 逐月对比
    """
    # 筛选当年记录
    year_records = [r for r in records if r.get("日期", "").startswith(f"{year}-")]

    # 逐月统计
    monthly_data = {}
    for m in range(1, 13):
        monthly = [r for r in year_records if r.get("日期", "").startswith(f"{year}-{m:02d}")]
        if not monthly:
            continue
        stats = monthly_stats(records, year, m)
        monthly_data[f"{year}-{m:02d}"] = {
            "total_days": stats["total_days"],
            "total_live_rounds": stats["total_live_rounds"],
            "total_train_min": stats["total_train_min"],
        }

    # 年度汇总
    total_rounds = sum_safe(year_records, key="实弹发数", cast=int)
    total_train_min = sum_safe(year_records, key="训练总时长(分钟)", cast=float)
    total_hours = total_train_min / 60

    return {
        "year": year,
        "total_days": len(year_records),
        "total_live_rounds": total_rounds,
        "total_live_rounds_formatted": rounds_to_string(total_rounds),
        "total_train_hours": round(total_hours, 1),
        "total_train_hours_formatted": minutes_to_hours(total_train_min),
        "training_volume_level": training_volume_classify(total_rounds, total_hours),
        "monthly_breakdown": monthly_data,
    }


def error_type_analysis(records: list) -> dict:
    """
    失误类型占比统计（基于备注字段的关键词分析）。

    Args:
        records: 训练记录列表（CSV 字典列表）

    Returns:
        失误类型分布 + 统计详情
    """
    # 失误关键词映射
    error_keywords = {
        "动作变形": ["变形", "动作不稳", "姿态偏移"],
        "散布偏大": ["偏", "散布", "偏差"],
        "呼吸不稳": ["呼吸", "屏息不足"],
        "心理波动": ["高压", "紧张", "心理", "情绪", "焦虑"],
        "体能下降": ["酸", "疲劳", "乏力", "体力"],
        "扳机控制": ["猛扣", "扳机", "扣动"],
    }

    error_counts = defaultdict(int)
    total_errors = 0
    error_details = []

    for r in records:
        note = r.get("备注", "")
        if not note:
            continue
        found_errors = []
        for error_type, keywords in error_keywords.items():
            for kw in keywords:
                if kw in note:
                    error_counts[error_type] += 1
                    found_errors.append(error_type)
                    break  # 每类只计一次
        if found_errors:
            total_errors += 1
            error_details.append({
                "日期": r.get("日期", ""),
                "备注": note,
                "失误类型": found_errors,
            })

    # 计算占比
    percentages = {}
    for err_type, count in error_counts.items():
        percentages[err_type] = round(count / total_errors * 100, 1) if total_errors else 0

    # 排序
    sorted_errors = sorted(percentages.items(), key=lambda x: -x[1])

    return {
        "total_error_days": total_errors,
        "error_distribution": {k: v for k, v in sorted_errors},
        "error_percentages": percentages,
        "error_details_sample": error_details[:10],  # 最多返回10条详情
    }


def progress_curve(records: list) -> dict:
    """
    进步曲线数据（返回可用于图表渲染的数据结构）。

    Args:
        records: 训练记录列表（CSV 字典列表）

    Returns:
        图表数据 {"dates": [...], "series": {"series_name": {"x": [...], "y": [...]}}}
    """
    # 按日期排序
    sorted_records = sorted(records, key=lambda r: r.get("日期", ""))

    dates = [r.get("日期", "") for r in sorted_records]

    # 实弹发数
    live_rounds = [int(r.get("实弹发数", 0) or 0) for r in sorted_records]

    # 空扣扳机次数
    empty_trigger = [int(r.get("空扣扳机次数", 0) or 0) for r in sorted_records]

    # 定型保持时长
    hold_time = [float(r.get("定型保持时长(分钟)", 0) or 0) for r in sorted_records]

    # 静息心率
    resting_hr = [int(r.get("静息心率(bpm)", 0) or 0) for r in sorted_records]

    # 屏息最长时长
    breath_hold = [int(r.get("屏息最长时长(秒)", 0) or 0) for r in sorted_records]

    return {
        "dates": dates,
        "series": {
            "实弹发数": {"x": dates, "y": live_rounds, "unit": "发"},
            "空扣扳机次数": {"x": dates, "y": empty_trigger, "unit": "次"},
            "定型保持时长": {"x": dates, "y": hold_time, "unit": "分钟"},
            "静息心率": {"x": dates, "y": resting_hr, "unit": "bpm"},
            "屏息最长时长": {"x": dates, "y": breath_hold, "unit": "秒"},
        },
        "trend_summary": {
            "hr_trend": "下降" if len(resting_hr) >= 2 and resting_hr[-1] < resting_hr[0] else "上升/持平",
            "hold_time_trend": "上升" if len(hold_time) >= 2 and hold_time[-1] > hold_time[0] else "持平/下降",
        },
    }


if __name__ == "__main__":
    # 通过 common 工具层加载训练记录
    records = load_csv("年度训练量化记录表.csv", subdir="tables")

    print("=== 月度统计（2026年7月）===")
    result = monthly_stats(records, 2026, 7)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n=== 年度汇总（2026年）===")
    annual = annual_summary(records, 2026)
    print(json.dumps(annual, ensure_ascii=False, indent=2))

    print("\n=== 失误类型分析 ===")
    errors = error_type_analysis(records)
    print(json.dumps(errors, ensure_ascii=False, indent=2))

    print("\n=== 进步曲线数据 ===")
    curve = progress_curve(records)
    print(json.dumps(curve, ensure_ascii=False, indent=2))
