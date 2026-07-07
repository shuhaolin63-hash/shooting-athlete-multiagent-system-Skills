# -*- coding: utf-8 -*-
"""通用数学计算工具模块。

提供射击训练评估中常用的数学计算函数，包括加权打分、
区间判断、等级分类、阈值对比、扣分计算等。

所有函数均为纯函数，不涉及任何 IO 操作。
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


def weighted_score(scores: Dict[str, float], weights: Dict[str, float]) -> Dict[str, Any]:
    """加权打分计算。

    根据各维度的得分和对应权重，计算加权总分、满分和百分比。

    Args:
        scores: 各维度得分字典，格式如 {"空枪基础定型": 85, "实弹射击实操": 72, ...}。
        weights: 各维度权重字典，格式如 {"空枪基础定型": 30, "实弹射击实操": 25, ...}。
                 权重值代表该维度的满分（非百分比权重）。

    Returns:
        包含以下键的字典：
        - 各维度的加权得分（key 为维度名）
        - "total": 加权总分
        - "max_total": 满分总和
        - "percentage": 百分比得分 (0~100)

    Example:
        >>> weighted_score({"A": 80, "B": 60}, {"A": 30, "B": 20})
        {'A': 80.0, 'B': 60.0, 'total': 140.0, 'max_total': 50.0, 'percentage': 280.0}

    Note:
        若权重总和为 0，percentage 返回 0 以避免除零错误。
    """
    result: Dict[str, Any] = {}
    total = 0.0
    max_total = 0.0

    for dim, score in scores.items():
        weight = weights.get(dim, 0)
        # 加权分 = 实际得分 * (该维度权重 / 满分100)
        weighted = score * (weight / 100.0)
        result[dim] = round(weighted, 2)
        total += weighted
        max_total += weight

    result["total"] = round(total, 2)
    result["max_total"] = round(max_total, 2)
    result["percentage"] = round((total / max_total * 100), 2) if max_total > 0 else 0.0

    return result


def in_range(value: float, min_val: float, max_val: float) -> bool:
    """判断值是否在指定区间内（闭区间）。

    Args:
        value: 待判断的数值。
        min_val: 区间下限（包含）。
        max_val: 区间上限（包含）。

    Returns:
        True 如果 value 在 [min_val, max_val] 范围内，否则 False。
    """
    return min_val <= value <= max_val


def classify_level(percentage: float, thresholds: Dict[str, float]) -> str:
    """根据百分比得分和阈值表判定等级。

    阈值表中的数值代表达到该等级所需的最低百分比。
    函数从高到低匹配，返回第一个满足条件的等级名称。

    Args:
        percentage: 百分比得分 (0~100)。
        thresholds: 等级阈值字典，格式如
                    {"国家队": 95, "国青": 80, "省赛": 60, "零基础合格": 40}。
                    数值越高等级越高。

    Returns:
        匹配到的等级名称字符串。若未匹配到任何等级，返回 "未评级"。

    Example:
        >>> classify_level(82, {"国家队": 95, "国青": 80, "省赛": 60})
        '国青'
    """
    # 按阈值从高到低排序
    sorted_levels = sorted(thresholds.items(), key=lambda x: x[1], reverse=True)

    for level_name, threshold in sorted_levels:
        if percentage >= threshold:
            return level_name

    return "未评级"


def mean(values: List[float]) -> float:
    """安全均值计算。

    Args:
        values: 数值列表。

    Returns:
        列表元素的算术平均值。空列表返回 0.0。
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


def sum_safe(values: List[Any], key: Optional[str] = None) -> float:
    """安全求和。

    支持对数值列表直接求和，也支持对字典列表按指定 key 求和。

    Args:
        values: 数值列表或字典列表。
        key: 若 values 为字典列表，指定用于求和的键名。

    Returns:
        求和结果。空列表返回 0.0。

    Example:
        >>> sum_safe([1, 2, 3])
        6.0
        >>> sum_safe([{"score": 80}, {"score": 90}], key="score")
        170.0
    """
    if not values:
        return 0.0

    if key is not None:
        return sum(float(v.get(key, 0)) for v in values)
    else:
        return sum(float(v) for v in values)


def compare_threshold(value: float, threshold_map: Dict[str, float]) -> Dict[str, Any]:
    """多级阈值对比。

    将数值与多级阈值进行对比，返回最匹配的等级和差距。

    Args:
        value: 待对比的数值。
        threshold_map: 阈值字典，格式如 {"优秀": 90, "良好": 70, "合格": 50}。
                      数值代表达到该等级所需的最低分数。

    Returns:
        包含以下键的字典：
        - "level": 匹配到的等级名称。
        - "gap": 与该等级阈值的差值（正值表示超出，负值表示不足）。

    Example:
        >>> compare_threshold(75, {"优秀": 90, "良好": 70, "合格": 50})
        {'level': '良好', 'gap': 5.0}
    """
    sorted_levels = sorted(threshold_map.items(), key=lambda x: x[1], reverse=True)

    for level_name, threshold in sorted_levels:
        if value >= threshold:
            return {
                "level": level_name,
                "gap": round(value - threshold, 2),
            }

    # 未达到任何等级，以最低等级为参照
    lowest_name, lowest_threshold = sorted_levels[-1]
    return {
        "level": lowest_name,
        "gap": round(value - lowest_threshold, 2),
    }


def deduction_score(
    base: float,
    rules: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """扣分计算。

    在基础分上按规则列表依次扣分，返回最终得分和扣分明细。

    Args:
        base: 基础分数。
        rules: 扣分规则列表，每条规则为字典，包含：
               - "condition": 一个 callable，接受当前剩余分数，返回 bool 表示是否触发扣分。
               - "deduction": 扣分数值。
               - "reason": 扣分原因描述。

    Returns:
        包含以下键的字典：
        - "final_score": 扣分后的最终得分（最低为 0）。
        - "deductions": 触发的扣分明细列表，每项为 {"reason": str, "amount": float}。

    Example:
        >>> base = 100
        >>> rules = [
        ...     {"condition": lambda x: x < 60, "deduction": 10, "reason": "低于60扣10分"},
        ...     {"condition": lambda x: True, "deduction": 5, "reason": "固定扣5分"},
        ... ]
        >>> deduction_score(base, rules)
        {'final_score': 95.0, 'deductions': [{'reason': '固定扣5分', 'amount': 5.0}]}
    """
    current = float(base)
    deductions: List[Dict[str, Any]] = []

    for rule in rules:
        condition_fn: Callable[[float], bool] = rule["condition"]
        deduction_amount: float = float(rule["deduction"])
        reason: str = rule["reason"]

        if condition_fn(current):
            current -= deduction_amount
            deductions.append({
                "reason": reason,
                "amount": deduction_amount,
            })

    # 最低为 0 分
    current = max(current, 0.0)

    return {
        "final_score": round(current, 2),
        "deductions": deductions,
    }


# ---------------------------------------------------------------------------
# 测试入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("math_calc.py 模块测试")
    print("=" * 60)

    # 1. weighted_score 测试
    print("\n[1] weighted_score 测试")
    scores = {"空枪基础定型": 85, "实弹射击实操": 72, "体能储备": 68, "心理素质": 80, "战术素养": 75}
    weights = {"空枪基础定型": 30, "实弹射击实操": 25, "体能储备": 15, "心理素质": 20, "战术素养": 10}
    ws = weighted_score(scores, weights)
    print(f"    输入得分: {scores}")
    print(f"    输入权重: {weights}")
    print(f"    结果: {ws}")

    # 2. in_range 测试
    print("\n[2] in_range 测试")
    print(f"    50 in [0, 100]: {in_range(50, 0, 100)}")
    print(f"   -10 in [0, 100]: {in_range(-10, 0, 100)}")
    print(f"   100 in [0, 100]: {in_range(100, 0, 100)}")

    # 3. classify_level 测试
    print("\n[3] classify_level 测试")
    thresholds = {"国家队": 95, "国青": 80, "省赛": 60, "零基础合格": 40}
    for pct in [96, 82, 60, 35]:
        level = classify_level(pct, thresholds)
        print(f"    {pct}% -> {level}")

    # 4. mean 测试
    print("\n[4] mean 测试")
    print(f"    mean([80, 90, 70]) = {mean([80, 90, 70])}")
    print(f"    mean([]) = {mean([])}")

    # 5. sum_safe 测试
    print("\n[5] sum_safe 测试")
    print(f"    sum_safe([1, 2, 3]) = {sum_safe([1, 2, 3])}")
    data = [{"score": 80}, {"score": 90}, {"score": 70}]
    print(f"    sum_safe(dict_list, key='score') = {sum_safe(data, key='score')}")

    # 6. compare_threshold 测试
    print("\n[6] compare_threshold 测试")
    for val in [95, 75, 45]:
        result = compare_threshold(val, {"优秀": 90, "良好": 70, "合格": 50})
        print(f"    {val} -> {result}")

    # 7. deduction_score 测试
    print("\n[7] deduction_score 测试")
    base = 100
    rules = [
        {"condition": lambda x: x < 60, "deduction": 10, "reason": "低于60扣10分"},
        {"condition": lambda x: True, "deduction": 5, "reason": "固定扣5分"},
    ]
    result = deduction_score(base, rules)
    print(f"    基础分: {base}")
    print(f"    结果: {result}")

    print("\n" + "=" * 60)
    print("所有测试完成")
    print("=" * 60)
