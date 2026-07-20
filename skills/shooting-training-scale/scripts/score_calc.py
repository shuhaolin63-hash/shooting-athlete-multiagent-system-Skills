# -*- coding: utf-8 -*-
"""量表总分计算、等级评级 - Scale-Eval-Agent 核心引擎

读取 scale-scoring-rules.yaml 配置，计算五维度加权得分，
判定等级，识别薄弱维度。
"""

import sys
import json
from pathlib import Path

# 确保可以导入 common 工具层
sys.path.insert(0, str(Path(__file__).parent))

from common.file_io import get_assets_dir, load_yaml
from common.math_calc import classify_level


def calc_score(scores: dict) -> dict:
    """
    计算五大维度综合得分并判定等级。

    Args:
        scores: 各维度实际得分字典
            {"aimless_foundation": 85, "live_fire": 72, "physical_fitness": 71,
             "mental_resilience": 65, "equipment_fitting": 88}

    Returns:
        包含 total, max_total, percentage, level, breakdown, weaknesses, deductions 的字典

    Raises:
        ValueError: scores 为空或包含非法值时
    """
    # 参数校验：空输入或非字典类型
    if not scores or not isinstance(scores, dict):
        raise ValueError(f"scores 必须为非空字典，收到: {type(scores).__name__}")

    # 通过 common 工具层读取 YAML 配置
    rules = load_yaml("scale-scoring-rules.yaml", subdir="config-rules")
    required_dims = set(rules.get("dimensions", {}).keys())

    # 检查必要维度是否存在
    missing = required_dims - set(scores.keys())
    if missing:
        raise ValueError(f"缺少必要维度: {missing}")

    # 检查得分值是否为非负数
    for dim, val in scores.items():
        if not isinstance(val, (int, float)) or val < 0:
            raise ValueError(f"维度 '{dim}' 得分无效: {val}（需为非负数字）")

    # 从 YAML 提取等级阈值（classify_level 期望 Dict[str, float]）
    level_cfg = rules.get("level_thresholds", {})
    levels = {v.get("label", k): v["min_percentage"] for k, v in level_cfg.items()}

    # 计算各维度得分
    total = 0
    max_total = 0
    breakdown = {}
    for dim_key, dim_cfg in rules["dimensions"].items():
        raw = scores.get(dim_key, 0)
        breakdown[dim_cfg["name"]] = {"score": raw, "max": dim_cfg["max_score"]}
        total += raw
        max_total += dim_cfg["max_score"]

    # 计算百分比
    pct = (total / max_total * 100) if max_total else 0

    # 使用 common 工具层判定等级
    level = classify_level(pct, levels)

    # 识别薄弱维度（得分率低于60%）
    weak_dims = [name for name, info in breakdown.items() if info["score"] / info["max"] < 0.6]

    # 扣分规则
    deduction_rules = rules.get("deduction_rules", {})
    deductions = list(deduction_rules.values()) if deduction_rules else []

    return {
        "total": total,
        "max_total": max_total,
        "percentage": round(pct, 1),
        "level": level,
        "breakdown": breakdown,
        "weaknesses": weak_dims,
        "deductions": deductions,
    }


def calc_score_from_file(scores_file: str) -> dict:
    """
    从 JSON 文件读取五维度得分数据并计算。

    Args:
        scores_file: JSON 文件绝对路径
            文件格式: {"aimless_foundation": 85, "live_fire": 72, ...}

    Returns:
        与 calc_score 相同的返回结构
    """
    with open(scores_file, "r", encoding="utf-8") as f:
        scores = json.load(f)
    return calc_score(scores)


if __name__ == "__main__":
    # 演示调用：传入五维度得分字典
    sample = {
        "aimless_foundation": 78,
        "live_fire": 82,
        "physical_fitness": 71,
        "mental_resilience": 65,
        "equipment_fitting": 88,
    }
    result = calc_score(sample)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n--- calc_score_from_file 演示 ---")
    print("（传入 JSON 文件路径即可从文件读取数据并计算）")
