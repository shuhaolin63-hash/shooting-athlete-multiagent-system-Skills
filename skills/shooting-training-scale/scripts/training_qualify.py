# -*- coding: utf-8 -*-
"""训练五大维度达标判定 - 对标国家队标准

校验每日训练是否达标，支持单日和批量（一周）校验。
"""

import sys
import json
from pathlib import Path

# 确保可以导入 common 工具层
sys.path.insert(0, str(Path(__file__).parent))

from common.file_io import get_assets_dir, load_yaml, load_csv
from common.math_calc import compare_threshold, mean
from common.unit_convert import hold_time_classify, rounds_to_string


# ─── 国家队达标标准（可由 YAML 覆盖） ───────────────────────

STANDARDS = {
    "aimless_foundation": {
        "daily_empty_trigger": {"threshold": 200, "direction": "higher", "unit": "次", "label": "空扣扳机次数"},
        "daily_hold_minutes": {"threshold": 15, "direction": "higher", "unit": "分钟", "label": "定型保持时长"},
        "daily_shell_stack": {"threshold": 3, "direction": "higher", "unit": "个", "label": "弹壳叠放"},
        "daily_breath_hold_sec": {"threshold": 8, "direction": "higher", "unit": "秒", "label": "屏息时长"},
    },
    "live_fire": {
        "daily_rounds": {"threshold": 60, "direction": "higher", "unit": "发", "label": "实弹发数"},
        "group_avg_9plus": {"threshold": 0.6, "direction": "higher", "unit": "比例", "label": "9环以上比例"},
        "repeatability_mm": {"threshold": 25, "direction": "lower", "unit": "mm", "label": "散布重复性"},
    },
    "physical_fitness": {
        "plank_sec": {"threshold": 90, "direction": "higher", "unit": "秒", "label": "平板支撑"},
        "side_plank_sec": {"threshold": 60, "direction": "higher", "unit": "秒", "label": "侧平板支撑"},
        "static_hold_min": {"threshold": 8, "direction": "higher", "unit": "分钟", "label": "静态持枪"},
        "single_leg_sec": {"threshold": 60, "direction": "higher", "unit": "秒", "label": "单脚站立"},
    },
    "mental_resilience": {
        "pressure_retain_pct": {"threshold": 0.8, "direction": "higher", "unit": "比例", "label": "高压保留率"},
        "visualization_score": {"threshold": 8, "direction": "higher", "unit": "分", "label": "表象评分"},
        "ritual_consistency": {"threshold": True, "direction": "bool", "unit": "", "label": "仪式一致性"},
    },
    "equipment_fitting": {
        "trigger_consistency_g": {"threshold": 20, "direction": "lower", "unit": "g", "label": "扳机一致性"},
        "stock_fit_score": {"threshold": 8, "direction": "higher", "unit": "分", "label": "枪托适配"},
        "suit_comfort_score": {"threshold": 8, "direction": "higher", "unit": "分", "label": "射击服舒适度"},
    },
}


def qualify_daily(record: dict) -> dict:
    """
    校验单日训练是否达标。

    Args:
        record: 单日训练数据，键名格式 "维度.指标"
            {"aimless_foundation.daily_empty_trigger": 250,
             "aimless_foundation.daily_hold_minutes": 18, ...}

    Returns:
        各维度达标详情 {"维度": {"passed": {...}, "pass_rate": 0.8}, ...}
    """
    results = {}
    for dim, stds in STANDARDS.items():
        passed = {}
        for key, cfg in stds.items():
            full_key = f"{dim}.{key}"
            val = record.get(full_key, None)
            if val is None:
                continue
            # 使用 common 工具层进行阈值比较
            if cfg["direction"] == "bool":
                passed[key] = (val == cfg["threshold"])
            else:
                passed[key] = compare_threshold(val, cfg["threshold"], cfg["direction"])

        total_checks = len(passed)
        pass_count = sum(1 for v in passed.values() if v)
        pass_rate = pass_count / total_checks if total_checks else 0

        # 格式化输出
        formatted = {}
        for key, is_pass in passed.items():
            cfg = stds[key]
            formatted[cfg["label"]] = {
                "达标": "是" if is_pass else "否",
                "方向": "≤" if cfg["direction"] == "lower" else "≥",
                "标准": cfg["threshold"],
            }

        results[dim] = {
            "passed": passed,
            "formatted": formatted,
            "pass_rate": round(pass_rate, 2),
            "summary": f"通过 {pass_count}/{total_checks} 项",
        }
    return results


def qualify_week(records: list) -> dict:
    """
    批量校验一周训练数据。

    Args:
        records: 一周的训练记录列表，每个元素为 qualify_daily 接受的 dict

    Returns:
        每日达标详情 + 周汇总 {"daily_results": [...], "weekly_summary": {...}}
    """
    daily_results = []
    week_pass_rates = []

    for i, record in enumerate(records):
        result = qualify_daily(record)
        # 计算当日整体通过率
        all_checks = []
        for dim_data in result.values():
            total = len(dim_data["passed"])
            passed = sum(1 for v in dim_data["passed"].values() if v)
            all_checks.extend([True] * passed + [False] * (total - passed))
        day_rate = sum(1 for v in all_checks if v) / len(all_checks) if all_checks else 0
        week_pass_rates.append(day_rate)

        daily_results.append({
            "day_index": i + 1,
            "result": result,
            "overall_pass_rate": round(day_rate, 2),
        })

    # 周汇总
    avg_rate = mean(week_pass_rates)
    qualified_days = sum(1 for r in week_pass_rates if r >= 0.7)

    weekly_summary = {
        "total_days": len(records),
        "qualified_days": qualified_days,
        "avg_pass_rate": avg_rate,
        "week_qualified": avg_rate >= 0.7,
        "training_volume": rounds_to_string(sum(r.get("live_fire.daily_rounds", 0) for r in records)),
    }

    return {
        "daily_results": daily_results,
        "weekly_summary": weekly_summary,
    }


if __name__ == "__main__":
    # 演示调用：单日校验
    sample = {
        "aimless_foundation.daily_empty_trigger": 250,
        "aimless_foundation.daily_hold_minutes": 18,
        "aimless_foundation.daily_breath_hold_sec": 10,
        "live_fire.daily_rounds": 60,
        "live_fire.group_avg_9plus": 0.7,
        "physical_fitness.plank_sec": 95,
        "physical_fitness.single_leg_sec": 70,
        "mental_resilience.pressure_retain_pct": 0.85,
        "mental_resilience.ritual_consistency": True,
        "equipment_fitting.trigger_consistency_g": 18,
    }
    result = qualify_daily(sample)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n--- qualify_week 演示 ---")
    week_records = [sample, sample, sample, sample, sample, sample, sample]
    week_result = qualify_week(week_records)
    print(json.dumps(week_result["weekly_summary"], ensure_ascii=False, indent=2))
