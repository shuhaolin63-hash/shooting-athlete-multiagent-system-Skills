# -*- coding: utf-8 -*-
"""射击保障团队完备度评分 - Team-Structure-Agent

审计保障团队角色配置是否完备，
支持单体制对比和三种体制同时对比。
"""

import sys
import json
from pathlib import Path

# 确保可以导入 common 工具层
sys.path.insert(0, str(Path(__file__).parent))

from common.file_io import get_assets_dir, load_json
from common.math_calc import classify_level


# ─── 评分等级配置 ───────────────────────────────────────────

AUDIT_LEVELS = {
    "优秀 - 接近世界第一配置": 90,
    "良好 - 基本满足训练需求": 70,
    "一般 - 存在明显短板": 50,
    "不足 - 需要大幅补强": 0,
}


def audit_team(current_team: list, team_type: str = "type_a_national") -> dict:
    """
    审计保障团队完备度。

    Args:
        current_team: 当前团队已有的角色键名列表
            ["head_coach", "assistant_coach", "fitness_coach", ...]
        team_type: 对比标准体制类型
            "type_a_national" / "type_b1_private" / "type_b2_association"

    Returns:
        评分详情 {"team_type", "current_roles", "score", "max_score",
                 "percentage", "rating", "missing_roles"}
    """
    # 通过 common 工具层读取 JSON 配置
    config = load_json("team-config-standard.json", subdir="config-rules")

    std = config["team_types"][team_type]
    weights = config["completeness_scoring"]["weights"]

    score = 0
    max_score = 0
    missing = []

    for role_info in std.get("required_roles", []):
        role_key = role_info["role"]
        if role_key in weights:
            max_score += weights[role_key]
        if role_key in current_team:
            score += weights.get(role_key, 0)
        else:
            missing.append(role_info["name"])

    pct = round(score / max_score * 100, 1) if max_score else 0

    # 使用 common 工具层判定评分等级
    rating = classify_level(pct, AUDIT_LEVELS)

    return {
        "team_type": std["name"],
        "team_type_key": team_type,
        "current_roles": current_team,
        "score": score,
        "max_score": max_score,
        "percentage": pct,
        "rating": rating,
        "missing_roles": missing,
        "optional_roles": [r["name"] for r in std.get("optional_roles", [])],
    }


def audit_all_types(current_team: list) -> dict:
    """
    同时对比三种体制（国家队/海外自费/协会共享）的完备度。

    Args:
        current_team: 当前团队已有的角色键名列表

    Returns:
        三种体制的对比结果 {"type_a_national": {...}, "type_b1_private": {...},
                           "type_b2_association": {...}, "recommendation": "..."}
    """
    team_types = {
        "type_a_national": "国家队体制",
        "type_b1_private": "海外自费私人",
        "type_b2_association": "协会共享极简",
    }

    results = {}
    best_type = None
    best_pct = -1

    for type_key, type_name in team_types.items():
        result = audit_team(current_team, type_key)
        results[type_key] = result
        if result["percentage"] > best_pct:
            best_pct = result["percentage"]
            best_type = type_key

    # 生成推荐
    recommendation = ""
    if best_pct >= 90:
        recommendation = f"当前团队配置优秀，最匹配「{team_types[best_type]}」标准"
    elif best_pct >= 70:
        recommendation = f"当前团队配置良好，建议参考「{team_types[best_type]}」标准补强"
    elif best_pct >= 50:
        recommendation = f"当前团队存在明显短板，建议重点补充: {results[best_type]['missing_roles']}"
    else:
        recommendation = f"当前团队严重不足，建议至少配置核心角色"

    return {
        "comparisons": results,
        "best_match": best_type,
        "best_percentage": best_pct,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    # 演示调用：传入当前团队角色
    sample = ["head_coach", "assistant_coach", "fitness_coach", "psychologist",
               "team_doctor", "armorer"]

    print("=== 单体制审计 ===")
    result = audit_team(sample)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n=== 三体制对比审计 ===")
    all_result = audit_all_types(sample)
    print(json.dumps(all_result, ensure_ascii=False, indent=2))
