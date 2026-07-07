# -*- coding: utf-8 -*-
"""身体机能选材指标校验 - Data-Calc-Agent

校验运动员身体机能指标是否达到各等级标准，
输出单项达标等级与综合评价。
"""

import sys
import json
from pathlib import Path

# 确保可以导入 common 工具层
sys.path.insert(0, str(Path(__file__).parent))

from common.file_io import get_assets_dir, load_yaml
from common.math_calc import classify_level

def _compare(val, threshold, direction):
    """内联阈值比较"""
    if direction == ">=":
        return val >= threshold
    elif direction == "<=":
        return val <= threshold
    elif direction == ">":
        return val > threshold
    elif direction == "<":
        return val < threshold
    return False
from common.unit_convert import bpm_classify, hold_time_classify


# ─── 身体指标阈值表 ─────────────────────────────────────────

THRESHOLDS = {
    "resting_hr": {
        "label": "静息心率", "unit": "bpm", "direction": "lower",
        "zero_base": 75, "provincial": 68, "national_youth": 62, "national_team": 55,
    },
    "single_leg_stance": {
        "label": "单脚站立", "unit": "sec", "direction": "higher",
        "zero_base": 15, "provincial": 30, "national_youth": 60, "national_team": 90,
    },
    "plank_hold": {
        "label": "平板支撑", "unit": "sec", "direction": "higher",
        "zero_base": 45, "provincial": 60, "national_youth": 90, "national_team": 120,
    },
    "static_hold": {
        "label": "静态持枪", "unit": "min", "direction": "higher",
        "zero_base": 3, "provincial": 5, "national_youth": 8, "national_team": 12,
    },
    "shoulder_width": {
        "label": "肩宽", "unit": "cm", "direction": "higher",
        "zero_base": 36, "provincial": 38, "national_youth": 40, "national_team": 42,
    },
    "wingspan": {
        "label": "臂展", "unit": "cm", "direction": "higher",
        "zero_base": ">=height", "provincial": ">=height+2",
        "national_youth": ">=height+5", "national_team": ">=height+8",
    },
    "shell_stack": {
        "label": "弹壳叠放", "unit": "pcs", "direction": "higher",
        "zero_base": 3, "provincial": 5, "national_youth": 8, "national_team": 12,
    },
    "trigger_precision": {
        "label": "扳机精度", "unit": "g", "direction": "lower",
        "zero_base": 50, "provincial": 30, "national_youth": 20, "national_team": 10,
    },
}

# 等级排序（用于逐级判断）
LEVEL_ORDER = ["national_team", "national_youth", "provincial", "zero_base"]

# 等级中文标签
LEVEL_LABELS = {
    "national_team": "国家队",
    "national_youth": "国青",
    "provincial": "省赛",
    "zero_base": "零基础合格",
}


def _determine_level(val, cfg) -> str:
    """
    判断单项指标达到的最高等级。

    Args:
        val: 实际测量值
        cfg: 指标阈值配置

    Returns:
        达到的等级键名
    """
    direction = cfg["direction"]
    for lvl in LEVEL_ORDER:
        threshold = cfg.get(lvl)
        # 跳过非数值阈值（如 ">=height"）
        if isinstance(threshold, str):
            continue
        if threshold is None:
            continue
        if _compare(val, threshold, direction):
            return lvl
    return "未达标"


def check_index(body_data: dict) -> dict:
    """
    校验身体机能选材指标。

    Args:
        body_data: 身体测量数据
            {"resting_hr": 65, "single_leg_stance": 45, "plank_hold": 85,
             "static_hold": 6, "shell_stack": 5, ...}

    Returns:
        各指标达标详情 + 综合评价
    """
    results = {}
    level_counts = {"national_team": 0, "national_youth": 0, "provincial": 0, "zero_base": 0, "未达标": 0}
    total_checked = 0

    for key, cfg in THRESHOLDS.items():
        val = body_data.get(key)
        if val is None:
            results[key] = {"label": cfg["label"], "status": "未测量", "value": None, "unit": cfg["unit"]}
            continue

        total_checked += 1
        reached = _determine_level(val, cfg)
        level_counts[reached] = level_counts.get(reached, 0) + 1

        # 使用 common 工具层做分类描述
        classify_desc = ""
        if key == "resting_hr" and isinstance(val, (int, float)):
            classify_desc = bpm_classify(val)
        elif key in ("static_hold",) and isinstance(val, (int, float)):
            classify_desc = hold_time_classify(val * 60)  # 分钟转秒

        result = {
            "label": cfg["label"],
            "status": reached,
            "status_label": LEVEL_LABELS.get(reached, reached),
            "value": val,
            "unit": cfg["unit"],
        }
        if classify_desc:
            result["classify_desc"] = classify_desc
        results[key] = result

    # 综合评价：以达标最多的等级为主等级
    main_level = max(level_counts, key=level_counts.get) if total_checked else "未测量"

    return {
        "items": results,
        "summary": {
            "total_items": len(THRESHOLDS),
            "checked_items": total_checked,
            "main_level": main_level,
            "main_level_label": LEVEL_LABELS.get(main_level, main_level),
            "level_distribution": level_counts,
        },
    }


if __name__ == "__main__":
    # 演示调用：传入身体指标数据
    sample = {
        "resting_hr": 65,
        "single_leg_stance": 45,
        "plank_hold": 85,
        "static_hold": 6,
        "shell_stack": 5,
        "trigger_precision": 25,
    }
    result = check_index(sample)
    print(json.dumps(result, ensure_ascii=False, indent=2))
